<?php
require_once 'db.php';
require_once 'lab_config.php';
require_once 'markdown.php';

$id = $_GET['id'] ?? null;

if (!$id) {
    die('Ticket ID required');
}

$id = (int) $id;
if ($id <= 0) {
    die('Ticket ID required');
}
$stmt = $db->prepare("SELECT * FROM tickets WHERE id = ?");
$stmt->bindValue(1, $id, SQLITE3_INTEGER);
$result = $stmt->execute();
$ticket = $result ? $result->fetchArray(SQLITE3_ASSOC) : false;

if (!$ticket) {
    die('Ticket not found');
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticket #<?php echo $id; ?></title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <header>
        <nav>
            <div class="container">
                <a href="/" class="logo">LMS Portal</a>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/portal/">Courses</a></li>
                    <li><a href="/support/">Create Ticket</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main class="container">
        <h1>Ticket #<?php echo htmlspecialchars($id); ?></h1>
        
        <div class="ticket-detail">
            <?php
            $format = $_GET['format'] ?? 'html';
            $use_markdown = ($format === 'md');

            if ($use_markdown) {
                $subject = render_markdown($ticket['subject']);
                $message = render_markdown($ticket['message']);
                $admin_notes = !empty($ticket['admin_notes']) ? render_markdown($ticket['admin_notes']) : '';
            } else {
                $subject = htmlspecialchars($ticket['subject']);
                $message = nl2br(htmlspecialchars($ticket['message']));
                $admin_notes = !empty($ticket['admin_notes']) ? nl2br(htmlspecialchars($ticket['admin_notes'])) : '';
            }
            ?>

            <h2><?php echo $subject; ?></h2>
            <p class="meta">Status: <?php echo htmlspecialchars($ticket['status']); ?> |
                Created: <?php echo htmlspecialchars($ticket['created_at']); ?></p>

            <div class="ticket-message">
                <?php echo $message; ?>
            </div>

            <?php if (!empty($ticket['admin_notes'])): ?>
            <div class="admin-notes">
                <h3>Admin Notes:</h3>
                <?php echo $admin_notes; ?>
            </div>
            <?php endif; ?>
        </div>

        
        <p><a href="/support/">← Back to Support</a></p>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 LMS Portal. Educational Lab Environment.</p>
        </div>
    </footer>
</body>
</html>
