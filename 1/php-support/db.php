<?php
$db_path = __DIR__ . '/support.db';
$db = new SQLite3($db_path);

error_reporting(E_ALL);
ini_set('display_errors', 1);
?>
