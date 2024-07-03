<?php


/***************************************************************************************
*    Title: How do I remove accents from characters in a PHP string?
*    Original implementation: https://github.com/WordPress/WordPress/blob/a2693fd8602e3263b5925b9d799ddd577202167d/wp-includes/formatting.php#L1528
*    Author: dynamic
*    Edited by: 8ctopus
*    Code version: 2021-02-15
*    Availability: https://stackoverflow.com/a/10790734
***************************************************************************************/
function remove_accents($string) {
	if ( !preg_match('/[\x80-\xff]/', $string) )
		return $string;

	$chars = array(
	// Decompositions for Latin-1 Supplement
	chr(195).chr(128) => 'A', chr(195).chr(129) => 'A',
	chr(195).chr(130) => 'A', chr(195).chr(131) => 'A',
	chr(195).chr(132) => 'A', chr(195).chr(133) => 'A',
	chr(195).chr(135) => 'C', chr(195).chr(136) => 'E',
	chr(195).chr(137) => 'E', chr(195).chr(138) => 'E',
	chr(195).chr(139) => 'E', chr(195).chr(140) => 'I',
	chr(195).chr(141) => 'I', chr(195).chr(142) => 'I',
	chr(195).chr(143) => 'I', chr(195).chr(145) => 'N',
	chr(195).chr(146) => 'O', chr(195).chr(147) => 'O',
	chr(195).chr(148) => 'O', chr(195).chr(149) => 'O',
	chr(195).chr(150) => 'O', chr(195).chr(153) => 'U',
	chr(195).chr(154) => 'U', chr(195).chr(155) => 'U',
	chr(195).chr(156) => 'U', chr(195).chr(157) => 'Y',
	chr(195).chr(159) => 's', chr(195).chr(160) => 'a',
	chr(195).chr(161) => 'a', chr(195).chr(162) => 'a',
	chr(195).chr(163) => 'a', chr(195).chr(164) => 'a',
	chr(195).chr(165) => 'a', chr(195).chr(167) => 'c',
	chr(195).chr(168) => 'e', chr(195).chr(169) => 'e',
	chr(195).chr(170) => 'e', chr(195).chr(171) => 'e',
	chr(195).chr(172) => 'i', chr(195).chr(173) => 'i',
	chr(195).chr(174) => 'i', chr(195).chr(175) => 'i',
	chr(195).chr(177) => 'n', chr(195).chr(178) => 'o',
	chr(195).chr(179) => 'o', chr(195).chr(180) => 'o',
	chr(195).chr(181) => 'o', chr(195).chr(182) => 'o',
	chr(195).chr(182) => 'o', chr(195).chr(185) => 'u',
	chr(195).chr(186) => 'u', chr(195).chr(187) => 'u',
	chr(195).chr(188) => 'u', chr(195).chr(189) => 'y',
	chr(195).chr(191) => 'y',
	// Decompositions for Latin Extended-A
	chr(196).chr(128) => 'A', chr(196).chr(129) => 'a',
	chr(196).chr(130) => 'A', chr(196).chr(131) => 'a',
	chr(196).chr(132) => 'A', chr(196).chr(133) => 'a',
	chr(196).chr(134) => 'C', chr(196).chr(135) => 'c',
	chr(196).chr(136) => 'C', chr(196).chr(137) => 'c',
	chr(196).chr(138) => 'C', chr(196).chr(139) => 'c',
	chr(196).chr(140) => 'C', chr(196).chr(141) => 'c',
	chr(196).chr(142) => 'D', chr(196).chr(143) => 'd',
	chr(196).chr(144) => 'D', chr(196).chr(145) => 'd',
	chr(196).chr(146) => 'E', chr(196).chr(147) => 'e',
	chr(196).chr(148) => 'E', chr(196).chr(149) => 'e',
	chr(196).chr(150) => 'E', chr(196).chr(151) => 'e',
	chr(196).chr(152) => 'E', chr(196).chr(153) => 'e',
	chr(196).chr(154) => 'E', chr(196).chr(155) => 'e',
	chr(196).chr(156) => 'G', chr(196).chr(157) => 'g',
	chr(196).chr(158) => 'G', chr(196).chr(159) => 'g',
	chr(196).chr(160) => 'G', chr(196).chr(161) => 'g',
	chr(196).chr(162) => 'G', chr(196).chr(163) => 'g',
	chr(196).chr(164) => 'H', chr(196).chr(165) => 'h',
	chr(196).chr(166) => 'H', chr(196).chr(167) => 'h',
	chr(196).chr(168) => 'I', chr(196).chr(169) => 'i',
	chr(196).chr(170) => 'I', chr(196).chr(171) => 'i',
	chr(196).chr(172) => 'I', chr(196).chr(173) => 'i',
	chr(196).chr(174) => 'I', chr(196).chr(175) => 'i',
	chr(196).chr(176) => 'I', chr(196).chr(177) => 'i',
	chr(196).chr(178) => 'IJ',chr(196).chr(179) => 'ij',
	chr(196).chr(180) => 'J', chr(196).chr(181) => 'j',
	chr(196).chr(182) => 'K', chr(196).chr(183) => 'k',
	chr(196).chr(184) => 'k', chr(196).chr(185) => 'L',
	chr(196).chr(186) => 'l', chr(196).chr(187) => 'L',
	chr(196).chr(188) => 'l', chr(196).chr(189) => 'L',
	chr(196).chr(190) => 'l', chr(196).chr(191) => 'L',
	chr(197).chr(128) => 'l', chr(197).chr(129) => 'L',
	chr(197).chr(130) => 'l', chr(197).chr(131) => 'N',
	chr(197).chr(132) => 'n', chr(197).chr(133) => 'N',
	chr(197).chr(134) => 'n', chr(197).chr(135) => 'N',
	chr(197).chr(136) => 'n', chr(197).chr(137) => 'N',
	chr(197).chr(138) => 'n', chr(197).chr(139) => 'N',
	chr(197).chr(140) => 'O', chr(197).chr(141) => 'o',
	chr(197).chr(142) => 'O', chr(197).chr(143) => 'o',
	chr(197).chr(144) => 'O', chr(197).chr(145) => 'o',
	chr(197).chr(146) => 'OE',chr(197).chr(147) => 'oe',
	chr(197).chr(148) => 'R',chr(197).chr(149) => 'r',
	chr(197).chr(150) => 'R',chr(197).chr(151) => 'r',
	chr(197).chr(152) => 'R',chr(197).chr(153) => 'r',
	chr(197).chr(154) => 'S',chr(197).chr(155) => 's',
	chr(197).chr(156) => 'S',chr(197).chr(157) => 's',
	chr(197).chr(158) => 'S',chr(197).chr(159) => 's',
	chr(197).chr(160) => 'S', chr(197).chr(161) => 's',
	chr(197).chr(162) => 'T', chr(197).chr(163) => 't',
	chr(197).chr(164) => 'T', chr(197).chr(165) => 't',
	chr(197).chr(166) => 'T', chr(197).chr(167) => 't',
	chr(197).chr(168) => 'U', chr(197).chr(169) => 'u',
	chr(197).chr(170) => 'U', chr(197).chr(171) => 'u',
	chr(197).chr(172) => 'U', chr(197).chr(173) => 'u',
	chr(197).chr(174) => 'U', chr(197).chr(175) => 'u',
	chr(197).chr(176) => 'U', chr(197).chr(177) => 'u',
	chr(197).chr(178) => 'U', chr(197).chr(179) => 'u',
	chr(197).chr(180) => 'W', chr(197).chr(181) => 'w',
	chr(197).chr(182) => 'Y', chr(197).chr(183) => 'y',
	chr(197).chr(184) => 'Y', chr(197).chr(185) => 'Z',
	chr(197).chr(186) => 'z', chr(197).chr(187) => 'Z',
	chr(197).chr(188) => 'z', chr(197).chr(189) => 'Z',
	chr(197).chr(190) => 'z', chr(197).chr(191) => 's'
	);

	$string = strtr($string, $chars);

	return $string;
}


$recipient = isset($_GET['recipient']) ? $_GET['recipient'] : '';


// price in format with max 2 decimal places
// example 1234.56
if (isset($_GET['price']))
	$price = $_GET['price'];
else
	// fail
	die('price is missing');

// payment note
// Accents like č, š, ž, etc. are stripped
if (isset($_GET['note']))
	$note = strtolower(remove_accents($_GET['note']));
else
	$note = '';

// account number (IBAN)
// example SK8011000000001234567890
// no spaces
// IMPORTANT - use your own account number, this example may not be working with your bank
if (isset($_GET['iban']))
	$iban = $_GET['iban'];
else
	// fail
	die('iban is missing');

// bank identifier code (BIC / swift)
// example TATRSKBX
if (isset($_GET['swift']))
	$swift = $_GET['swift'];
else
	// fail
	die('swift is missing');

// todays date in format yyyymmdd
// example 20170101
$date = date('Ymd');

// variable symbol
// max 10 digits
// numbers only
// example 1234567890
if (isset($_GET['vs']))
	$vs = $_GET['vs'];
else
	$vs = '';

// constant symbol
// max 4 digits
// numbers only
// example 1234
if (isset($_GET['cs']))
	$ks = $_GET['cs'];
else
	$ks = '';

// specific symbol
// max 10 digits
// numbers only
// example 1234567890
if (isset($_GET['ss']))
	$ss = $_GET['ss'];
else
	$ss = '';




// TODO: validate input




/***************************************************************************************
*    Title: QR GENERÁTOR PLATIEB PAY BY SQUARE V PHP
*    Author: Ján Fečík
*    Code version: 2016-12-04
*    Availability: https://jan.fecik.sk/blog/qr-generator-platieb-pay-by-square-v-php/
***************************************************************************************/
$d = implode("\t", array(
	0 => '',
	1 => '1',
	2 => implode("\t", array(
		true,
		$price,						// SUMA
		'EUR',						// JEDNOTKA
		$date,						// DATUM
		$vs,						// VARIABILNY SYMBOL
		$ks,						// KONSTANTNY SYMBOL
		$ss,						// SPECIFICKY SYMBOL
		'',
		$note,						// POZNAMKA
		'1',
		$iban,	// IBAN
		$swift,						// SWIFT
		'0',
		'0',
		$recipient
	))
));
$d = strrev(hash("crc32b", $d, TRUE)) . $d;
$x = proc_open("/usr/bin/xz '--format=raw' '--lzma1=lc=3,lp=0,pb=2,dict=128KiB' '-c' '-'", [0 => ["pipe", "r"], 1 => ["pipe", "w"]], $p);
fwrite($p[0], $d);
fclose($p[0]);
$o = stream_get_contents($p[1]);
fclose($p[1]);
proc_close($x);
$d = bin2hex("\x00\x00" . pack("v", strlen($d)) . $o);
$b = "";
for ($i = 0;$i < strlen($d);$i++) {
	$b .= str_pad(base_convert($d[$i], 16, 2), 4, "0", STR_PAD_LEFT);
}
$l = strlen($b);
$r = $l % 5;
if ($r > 0) {
	$p = 5 - $r;
	$b .= str_repeat("0", $p);
	$l += $p;
}
$l = $l / 5;
$d = str_repeat("_", $l);
for ($i = 0;$i < $l;$i += 1) {
	$d[$i] = "0123456789ABCDEFGHIJKLMNOPQRSTUV"[bindec(substr($b, $i * 5, 5))];
}




/***************************************************************************************
 *   Title: PHP QR Code encoder
 *   Author: Alexandre Assouad (t0k4rt)
 *   Code version: 2021-09-27
 *   Availability: https://github.com/t0k4rt/phpqrcode
***************************************************************************************/
include('phpqrcode/qrlib.php');
QRcode::png($d, false, QR_ECLEVEL_L, 1, 0);