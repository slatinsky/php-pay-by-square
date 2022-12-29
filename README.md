![](assets/example.png)

# PHP Pay by square
Umožňuje vytvárať jednoduché QR kódy pre platby Pay by square. Len prekopírujete na PHP hosting a máte hotovo :)

## Závislosti
- Len pre linuxový server - `/usr/bin/xz` musí existovať
- Testované s PHP 8 na Webhostingu Websupport.sk

## Inštalácia
- Nakopírujte obsah repozitára na váš hosting
- hlavny súbor je `qr.php`, ktorý je potrebné zavolať s parametrami (viac nižšie)

## Použitie na frontende
HTML:
```html
<img class="qr-image" src="https://qr.example.com/qr.php?price=5.01&note=jozko+mrkvicka&iban=SK7700000000000000000000&swift=CEKOSKBX&vs=00000002&ss=2022&cs=0000" alt="">
<br>
<img class="qr-image-square" src="https://qr.example.com/assets/paybysquare.png" alt="">
```

CSS:
```css
.qr-image {
    border: 5px solid #6FA4D7;
    max-width: 300px;
    width: 100%;
    height: auto;
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
    padding: 20px;
    margin: 20px;
    border-radius: 5px;
}

.qr-image-square {
    max-width: 300px;
    width: 100%;
    margin: 5px 20px;
}
```

## Parametre pre qr.php
| **Parameter** | **Popis**                             | **Ukážka**               | **Obmedzenie**           |
|---------------|---------------------------------------|--------------------------|--------------------------|
| price         | Cena                                  | 5.01                     | Max 2 desatinné miesta   |
| note          | Poznámka k platbe                     | jozko+mrkvicka           | Max 35 znakov            |
| iban          | Číslo účtu (IBAN)                     | SK7700000000000000000000 | Bez medzier              |
| swift         | Bankový identifikačný kód (BIC/SWIFT) | CEKOSKBX                 |                          |
| vs            | Variabilný symbol                     | 00000002                 | Len čísla, max 10 znakov |
| ss            | Špecifický symbol                     | 2022                     | Len čísla, max 10 znakov |
| cs            | Konštantný symbol                     | 0000                     | Len čísla, max 4 znaky   |

Dátum splatnosti je automaticky nastavený na aktuálny deň

## FAQ
Nejde načítať QR kód v internet bankingu
- Ukážkový QR kód nefunguje pre každú banku, pretože niektoré overujú existenciu IBANu (a ukážkový IBAN SK7700000000000000000000 neexistuje). Vložte svoj vlastný IBAN a vyskúšajte znova :)

## Poďakovanie
- [Ján Fečík](https://jan.fecik.sk/blog/qr-generator-platieb-pay-by-square-v-php/) za implementáciu algoritmu Pay by square v PHP, z ktorého bol tento projekt forknutý
- [Alexandre Assouad (t0k4rt)](https://github.com/t0k4rt/phpqrcode) za generátor QR kódov


## Licencia
GNU General Public License v3.0

Pull requesty sú vítané :)

Ak sa vám projekt páči, ohodnoťte ho hviezdičkou ⭐️
