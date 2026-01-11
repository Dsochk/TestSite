<?php
function render_markdown($text) {
    $text = preg_replace('/^### (.+)$/m', '<h3>$1</h3>', $text);
    $text = preg_replace('/^## (.+)$/m', '<h2>$1</h2>', $text);
    $text = preg_replace('/^# (.+)$/m', '<h1>$1</h1>', $text);
    $text = preg_replace('/\\*\\*(.+?)\\*\\*/s', '<strong>$1</strong>', $text);
    $text = preg_replace('/\\*(.+?)\\*/s', '<em>$1</em>', $text);
    $text = preg_replace('/`(.+?)`/s', '<code>$1</code>', $text);
    $text = preg_replace('/\\[(.+?)\\]\\((.+?)\\)/s', '<a href=\"$2\">$1</a>', $text);
    return nl2br($text);
}
?>
