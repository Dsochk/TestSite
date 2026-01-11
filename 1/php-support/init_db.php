<?php
$db_path = __DIR__ . '/support.db';

if (file_exists($db_path)) {
    unlink($db_path);
}

$db = new SQLite3($db_path);

$db->exec("CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    admin_notes TEXT
)");

$db->exec("CREATE TABLE IF NOT EXISTS admin_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)");

$admin_session = 'admin_' . bin2hex(random_bytes(16));
$stmt = $db->prepare("INSERT INTO admin_sessions (session_id) VALUES (?)");
$stmt->bindValue(1, $admin_session, SQLITE3_TEXT);
$stmt->execute();

$sample_tickets = [
    ['subject' => 'Welcome', 'message' => 'This is a sample ticket'],
    ['subject' => 'Test Ticket', 'message' => 'Testing the support system']
];

foreach ($sample_tickets as $ticket) {
    $stmt = $db->prepare("INSERT INTO tickets (subject, message) VALUES (?, ?)");
    $stmt->bindValue(1, $ticket['subject'], SQLITE3_TEXT);
    $stmt->bindValue(2, $ticket['message'], SQLITE3_TEXT);
    $stmt->execute();
}

echo "Database initialized successfully!\n";
echo "Admin session: $admin_session\n";
?>
