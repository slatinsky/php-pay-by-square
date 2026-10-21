"""Black-box tests for the app served by Docker (see run.sh).

Generated QR codes are decoded with zbar and their payload is checked against
"PAY by square specifications 1.2.0" published by the Slovak Banking Association:
https://www.sbaonline.sk/projekt/projekty-z-oblasti-platobnych-sluzieb/
"""

import io
import lzma
import os
import struct
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
import zlib
from email.utils import parsedate_to_datetime

from PIL import Image, ImageOps

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")

# usage example from README.md
README_QUERY = (
    "price=5.01&note=pre%20jozka&iban=SK7700000000000000000000&swift=CEKOSKBX"
    "&vs=00000002&ss=2022&cs=0000&recipient=jozko%20mrkvicka&pixelsize=1&pixelpadding=0"
)

REQUIRED = {
    "price": "5.01",
    "iban": "SK7700000000000000000000",
    "swift": "CEKOSKBX",
    "recipient": "Jozko Mrkvicka",
}

QR_PNG_MAXIMUM_SIZE = 1024  # phpqrcode/qrconfig.php

# spec 3.13, table 9
BASE32HEX = "0123456789ABCDEFGHIJKLMNOPQRSTUV"

# spec appendix D, table 15
PAYMENT_FIELDS = (
    "PaymentOptions", "Amount", "CurrencyCode", "PaymentDueDate", "VariableSymbol",
    "ConstantSymbol", "SpecificSymbol", "OriginatorsReferenceInformation", "PaymentNote",
)
STANDING_ORDER_FIELDS = ("Day", "Month", "Periodicity", "LastDate")
DIRECT_DEBIT_FIELDS = (
    "DirectDebitScheme", "DirectDebitType", "VariableSymbol", "SpecificSymbol",
    "OriginatorsReferenceInformation", "MandateID", "CreditorID", "ContractID",
    "MaxAmount", "ValidTillDate",
)
BENEFICIARY_FIELDS = ("BeneficiaryName", "BeneficiaryAddressLine1", "BeneficiaryAddressLine2")


def get(path, params=None):
    """Return (status, headers, body). params is a dict or an already encoded query string."""
    url = BASE_URL + path
    if params is not None:
        url += "?" + (params if isinstance(params, str) else urllib.parse.urlencode(params))
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


def setUpModule():
    deadline = time.monotonic() + 30
    while True:
        try:
            get("/")
            return
        except OSError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def read_qr(modules):
    """Decode a QR code image with one pixel per module, adding the quiet zone zbar needs."""
    image = ImageOps.expand(modules, border=4, fill=255)
    image = image.resize((image.width * 4, image.height * 4), Image.NEAREST)
    with tempfile.NamedTemporaryFile(suffix=".png") as file:
        image.save(file, "PNG")
        file.flush()
        result = subprocess.run(
            ["zbarimg", "--quiet", "--raw", "-Sdisable", "-Sqrcode.enable", file.name],
            capture_output=True, text=True, check=True,
        )
    return result.stdout.rstrip("\n")


def decode_bysquare(text):
    """Reverse spec sections 3.10-3.13. Return (header, field sequence)."""
    bits = "".join(f"{BASE32HEX.index(char):05b}" for char in text)
    bits = bits[: len(bits) - len(bits) % 8]
    data = int(bits, 2).to_bytes(len(bits) // 8, "big")
    header, (size,), compressed = data[:2], struct.unpack("<H", data[2:4]), data[4:]
    decompressed = lzma.decompress(
        compressed,
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA1, "lc": 3, "lp": 0, "pb": 2, "dict_size": 128 * 1024}],
    )
    if len(decompressed) != size:
        raise ValueError(f"length in header is {size}, decompressed {len(decompressed)} bytes")
    (crc,), sequence = struct.unpack("<I", decompressed[:4]), decompressed[4:]
    if crc != zlib.crc32(sequence):
        raise ValueError("CRC32 checksum mismatch")
    return header, sequence.decode("utf-8")


def parse_pay(sequence):
    """Map a tab separated field sequence onto the data model (spec 3.8, appendix D and E)."""
    values = iter(sequence.split("\t"))

    def take():
        try:
            return next(values)
        except StopIteration:
            raise ValueError(f"field sequence ended early: {sequence!r}") from None

    document = {"InvoiceID": take(), "Payments": []}
    for _ in range(int(take())):
        payment = {field: take() for field in PAYMENT_FIELDS}
        payment["BankAccounts"] = [{"IBAN": take(), "BIC": take()} for _ in range(int(take()))]
        if take() == "1":
            payment["StandingOrderExt"] = {field: take() for field in STANDING_ORDER_FIELDS}
        if take() == "1":
            payment["DirectDebitExt"] = {field: take() for field in DIRECT_DEBIT_FIELDS}
        document["Payments"].append(payment)
    # beneficiary fields follow all payments, trailing empty ones may be left out
    for payment in document["Payments"]:
        payment.update({field: next(values, "") for field in BENEFICIARY_FIELDS})
    leftover = list(values)
    if leftover:
        raise ValueError(f"unexpected fields after the last payment: {leftover}")
    return document


def expected_payment(due_date, **fields):
    payment = {
        "PaymentOptions": "1",  # paymentorder
        "Amount": REQUIRED["price"],
        "CurrencyCode": "EUR",
        "PaymentDueDate": due_date,
        "VariableSymbol": "",
        "ConstantSymbol": "",
        "SpecificSymbol": "",
        "OriginatorsReferenceInformation": "",
        "PaymentNote": "",
        "BankAccounts": [{"IBAN": REQUIRED["iban"], "BIC": REQUIRED["swift"]}],
        "BeneficiaryName": REQUIRED["recipient"],
        "BeneficiaryAddressLine1": "",
        "BeneficiaryAddressLine2": "",
    }
    payment.update(fields)
    return payment


def render(modules, pixelsize, pixelpadding):
    """Expected qr.php output for the given module image."""
    image = ImageOps.expand(modules, border=pixelpadding, fill=255)
    return image.resize((image.width * pixelsize, image.height * pixelsize), Image.NEAREST)


class QrTestCase(unittest.TestCase):
    def fetch_png(self, params):
        status, headers, body = get("/qr.php", params)
        self.assertEqual(status, 200)
        self.assertEqual(headers.get_content_type(), "image/png", body[:500])
        return body, headers

    def fetch_image(self, params):
        body, _ = self.fetch_png(params)
        return Image.open(io.BytesIO(body)).convert("L")

    def fetch_modules(self, params):
        """Fetch a code at the default pixelsize 1 and pixelpadding 0, one pixel per module."""
        modules = self.fetch_image(params)
        self.assertEqual(modules.width, modules.height)
        self.assertIn(modules.width, range(21, 178, 4))  # QR versions 1-40
        self.assertLessEqual(set(modules.getdata()), {0, 255})
        return modules

    def fetch_document(self, params):
        """Return (header, document, today) where today is the server date as YYYYMMDD."""
        modules = self.fetch_modules(params)
        _, headers = self.fetch_png(params)
        text = read_qr(modules)
        self.assertRegex(text, r"^[0-9A-V]+$")  # QR alphanumeric mode subset
        header, sequence = decode_bysquare(text)
        today = parsedate_to_datetime(headers["Date"]).strftime("%Y%m%d")
        return header, parse_pay(sequence), today

    def assertImageEqual(self, actual, expected):
        self.assertEqual(actual.size, expected.size)
        self.assertEqual(actual.tobytes(), expected.tobytes())


class ErrorTestCase(QrTestCase):
    def assertError(self, params, message):
        status, headers, body = get("/qr.php", params)
        self.assertEqual(status, 200)
        self.assertNotEqual(headers.get_content_type(), "image/png")
        self.assertEqual(body.decode(), message)


class RequiredParametersTest(ErrorTestCase):
    def test_no_parameters(self):
        self.assertError({}, "price is missing")

    def test_missing_required_parameter(self):
        for missing in REQUIRED:
            with self.subTest(missing=missing):
                params = {name: value for name, value in REQUIRED.items() if name != missing}
                self.assertError(params, f"{missing} is missing")

    def test_empty_recipient(self):
        # BeneficiaryName is required since spec 1.2.0
        self.assertError({**REQUIRED, "recipient": ""}, "recipient is missing")


class ValidationTest(ErrorTestCase):
    def test_invalid_values_are_rejected(self):
        for name, value, message in [
            ("price", "", "price must be a number with max 2 decimal places"),
            ("price", "5,01", "price must be a number with max 2 decimal places"),
            ("price", "5.001", "price must be a number with max 2 decimal places"),
            ("price", "-5", "price must be a number with max 2 decimal places"),
            ("price", "1e3", "price must be a number with max 2 decimal places"),
            ("price", "5.01\n", "price must be a number with max 2 decimal places"),
            ("price", "1234567890123", "price must be a number with max 2 decimal places"),
            ("iban", "SK77 0000 0000 0000 0000 0000", "iban must be max 34 uppercase letters and digits without spaces"),
            ("iban", "sk7700000000000000000000", "iban must be max 34 uppercase letters and digits without spaces"),
            ("iban", "SK77" + "0" * 31, "iban must be max 34 uppercase letters and digits without spaces"),
            ("swift", "CEKOSKB", "swift must be 8 or 11 uppercase letters and digits"),
            ("swift", "CEKOSKBXX", "swift must be 8 or 11 uppercase letters and digits"),
            ("swift", "cekoskbx", "swift must be 8 or 11 uppercase letters and digits"),
            ("vs", "12345678901", "vs must be max 10 digits"),
            ("vs", "ABC", "vs must be max 10 digits"),
            ("ss", "12345678901", "ss must be max 10 digits"),
            ("cs", "12345", "cs must be max 4 digits"),
            ("cs", "03\t08", "cs must be max 4 digits"),
            ("note", "x" * 141, "note must be UTF-8 text with max 140 characters"),
            ("note", "\xe8", "note must be UTF-8 text with max 140 characters"),
            ("recipient", "x" * 71, "recipient must be UTF-8 text with max 70 characters"),
            ("recipient", "\xe8", "recipient must be UTF-8 text with max 70 characters"),
        ]:
            with self.subTest(**{name: value}):
                query = urllib.parse.urlencode({**REQUIRED, name: value}, encoding="latin-1")
                self.assertError(query, message)

    def test_arrays_are_rejected(self):
        self.assertError(urllib.parse.urlencode(REQUIRED) + "&note[]=x", "parameters must not be arrays")

    def test_values_at_limits_are_accepted(self):
        params = {
            "price": "123456789012.34",
            "iban": "SK77" + "1234567890" * 3,
            "swift": "TATRSKBX123",
            "vs": "1234567890",
            "cs": "1234",
            "ss": "1234567890",
            "note": "ž" * 140,
            "recipient": "Ž" * 70,
        }
        _, document, today = self.fetch_document(params)
        self.assertEqual(document["Payments"], [expected_payment(
            today,
            Amount="123456789012.34",
            BankAccounts=[{"IBAN": "SK77" + "1234567890" * 3, "BIC": "TATRSKBX123"}],
            VariableSymbol="1234567890",
            ConstantSymbol="1234",
            SpecificSymbol="1234567890",
            PaymentNote="z" * 140,
            BeneficiaryName="Ž" * 70,
        )])

    def test_tabs_are_replaced_with_spaces(self):
        # spec 3.8, otherwise a tab would shift the following fields
        params = {
            **REQUIRED,
            "note": "dakujem\t1\tSK0000000000000000000666\tATTACKER",
            "recipient": "Jozko\tMrkvicka",
        }
        _, document, today = self.fetch_document(params)
        self.assertEqual(document["Payments"], [expected_payment(
            today,
            PaymentNote="dakujem 1 sk0000000000000000000666 attacker",
            BeneficiaryName="Jozko Mrkvicka",
        )])


class PayloadTest(QrTestCase):
    def test_readme_example(self):
        _, document, today = self.fetch_document(README_QUERY)
        self.assertEqual(document, {
            "InvoiceID": "",
            "Payments": [expected_payment(
                today,
                VariableSymbol="00000002",
                ConstantSymbol="0000",
                SpecificSymbol="2022",
                PaymentNote="pre jozka",
                BeneficiaryName="jozko mrkvicka",
            )],
        })

    def test_header(self):
        header, _, _ = self.fetch_document(REQUIRED)
        # BySquareType 0 (PAY), version 0, DocumentType 0, reserved 0
        self.assertEqual(header, b"\x00\x00")

    def test_optional_parameters_default_to_empty(self):
        _, document, today = self.fetch_document(REQUIRED)
        self.assertEqual(document, {"InvoiceID": "", "Payments": [expected_payment(today)]})

    def test_values_are_passed_through(self):
        params = {
            **REQUIRED,
            "price": "1234.56",
            "iban": "SK3112000000198742637541",
            "swift": "SUBASKBX",
            "vs": "1234567890",
            "cs": "0308",
            "ss": "9876543210",
        }
        _, document, today = self.fetch_document(params)
        self.assertEqual(document["Payments"], [expected_payment(
            today,
            Amount="1234.56",
            BankAccounts=[{"IBAN": "SK3112000000198742637541", "BIC": "SUBASKBX"}],
            VariableSymbol="1234567890",
            ConstantSymbol="0308",
            SpecificSymbol="9876543210",
        )])

    def test_note_is_lowercased_and_stripped_of_accents(self):
        note = "Ľščťžýáíéúäňôŕĺď ĽŠČŤŽÝÁÍÉÚÄŇÔŔĹĎ Faktúra 2026/10"
        _, document, _ = self.fetch_document({**REQUIRED, "note": note})
        self.assertEqual(
            document["Payments"][0]["PaymentNote"],
            "lsctzyaieuanorld lsctzyaieuanorld faktura 2026/10",
        )

    def test_recipient_is_kept_as_is(self):
        recipient = "Jožko Mrkvička, s.r.o."
        _, document, _ = self.fetch_document({**REQUIRED, "recipient": recipient})
        self.assertEqual(document["Payments"][0]["BeneficiaryName"], recipient)

    def test_long_note_and_recipient(self):
        # maximum lengths from spec table 15, needs a bigger QR version than the defaults
        note = ("faktura c. 2026-0042 za webhosting, domenu a spravu servera "
                "pre obdobie oktober az december 2026 (variabilny symbol 20260042), dakujeme vam!")
        recipient = "Jozko Mrkvicka - Webove sluzby a programovanie na mieru, s.r.o. Kosice"
        self.assertEqual((len(note), len(recipient)), (140, 70))
        params = {**REQUIRED, "note": note, "recipient": recipient}
        _, document, _ = self.fetch_document(params)
        self.assertEqual(document["Payments"][0]["PaymentNote"], note)
        self.assertEqual(document["Payments"][0]["BeneficiaryName"], recipient)
        self.assertGreater(self.fetch_modules(params).width, self.fetch_modules(REQUIRED).width)

    def test_repeated_request_returns_same_image(self):
        # the second request reads phpqrcode masks cached by the first one
        params = {**REQUIRED, "note": "cache test"}
        self.assertEqual(self.fetch_png(params)[0], self.fetch_png(params)[0])


class ImageTest(QrTestCase):
    def test_default_is_one_pixel_per_module_without_padding(self):
        modules = self.fetch_modules(REQUIRED)
        self.assertEqual(modules.getpixel((0, 0)), 0)  # finder pattern touches the corner

    def test_pixelsize_and_pixelpadding(self):
        modules = self.fetch_modules(REQUIRED)
        for pixelsize, pixelpadding in [(1, 0), (2, 0), (1, 4), (4, 4), (10, 2)]:
            with self.subTest(pixelsize=pixelsize, pixelpadding=pixelpadding):
                image = self.fetch_image({**REQUIRED, "pixelsize": pixelsize, "pixelpadding": pixelpadding})
                self.assertImageEqual(image, render(modules, pixelsize, pixelpadding))

    def test_size_is_limited_to_png_maximum(self):
        modules = self.fetch_modules(REQUIRED)
        for pixelsize, pixelpadding in [(50, 0), (50, 50), (1000, 0)]:
            with self.subTest(pixelsize=pixelsize, pixelpadding=pixelpadding):
                image = self.fetch_image({**REQUIRED, "pixelsize": pixelsize, "pixelpadding": pixelpadding})
                fitting = QR_PNG_MAXIMUM_SIZE // (modules.width + 2 * pixelpadding)
                self.assertImageEqual(image, render(modules, min(pixelsize, fitting), pixelpadding))
                self.assertLessEqual(image.width, QR_PNG_MAXIMUM_SIZE)

    def test_invalid_values_fall_back_to_limits(self):
        for given, same_as in [
            ({"pixelsize": "0"}, {"pixelsize": "1"}),
            ({"pixelsize": "-5"}, {"pixelsize": "1"}),
            ({"pixelsize": "abc"}, {"pixelsize": "1"}),
            ({"pixelpadding": "-1"}, {"pixelpadding": "0"}),
            ({"pixelpadding": "abc"}, {"pixelpadding": "0"}),
            ({"pixelpadding": "51"}, {"pixelpadding": "50"}),
        ]:
            with self.subTest(**given):
                self.assertEqual(self.fetch_png({**REQUIRED, **given})[0], self.fetch_png({**REQUIRED, **same_as})[0])


class StaticFilesTest(unittest.TestCase):
    def test_demo_page_and_assets(self):
        for path, content_type in [
            ("/", "text/html"),
            ("/assets/qr.css", "text/css"),
            ("/assets/qr-demo.css", "text/css"),
            ("/assets/card.svg", "image/svg+xml"),
            ("/assets/example.png", "image/png"),
        ]:
            with self.subTest(path=path):
                status, headers, _ = get(path)
                self.assertEqual(status, 200)
                self.assertEqual(headers.get_content_type(), content_type)


if __name__ == "__main__":
    unittest.main()
