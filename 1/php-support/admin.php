<?php
require_once 'db.php';
require_once 'lab_config.php';

session_start();

$admin_cookie = $_COOKIE['admin_session'] ?? '';
$is_admin = false;

if ($admin_cookie) {
    $stmt = $db->prepare("SELECT * FROM admin_sessions WHERE session_id = ?");
    $stmt->bindValue(1, $admin_cookie, SQLITE3_TEXT);
    $result = $stmt->execute();
    $session = $result->fetchArray(SQLITE3_ASSOC);
    $is_admin = ($session !== false);
}

if (isset($_GET['steal'])) {
    $stolen_cookie = $_GET['steal'];
    $log_entry = date('c') . " " . $stolen_cookie . PHP_EOL;
    file_put_contents(__DIR__ . '/stolen.log', $log_entry, FILE_APPEND | LOCK_EX);
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $password = $_POST['password'] ?? '';
    $password_hash = $LAB_CONFIG['PHP_ADMIN_PASSWORD_HASH'] ?? '';

    if ($password_hash && password_verify($password, $password_hash)) {
        $session_id = 'admin_' . bin2hex(random_bytes(16));
        setcookie('admin_session', $session_id, time() + 3600, '/');
        
        $stmt = $db->prepare("INSERT INTO admin_sessions (session_id) VALUES (?)");
        $stmt->bindValue(1, $session_id, SQLITE3_TEXT);
        $stmt->execute();
        
        header('Location: admin.php');
        exit;
    } elseif (!$password_hash) {
        $error = 'Admin credentials are not configured';
    } else {
        $error = 'Invalid password';
    }
}

if ($is_admin && isset($_GET['action'])) {
    $action = $_GET['action'];
    $ticket_id = $_GET['ticket_id'] ?? null;
    
    if ($action === 'close' && $ticket_id) {
        $stmt = $db->prepare("UPDATE tickets SET status = 'closed' WHERE id = ?");
        $stmt->bindValue(1, $ticket_id, SQLITE3_INTEGER);
        $stmt->execute();
        header('Location: admin.php');
        exit;
    }
    
    if ($action === 'add_note' && $ticket_id && isset($_POST['note'])) {
        $note = $_POST['note'];
        $stmt = $db->prepare("UPDATE tickets SET admin_notes = ? WHERE id = ?");
        $stmt->bindValue(1, $note, SQLITE3_TEXT);
        $stmt->bindValue(2, $ticket_id, SQLITE3_INTEGER);
        $stmt->execute();
        header('Location: admin.php');
        exit;
    }
}

$tickets = [];
$result = $db->query("SELECT * FROM tickets ORDER BY created_at DESC");
while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
    $tickets[] = $row;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Support Admin Panel</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <header>
        <nav>
            <div class="container">
                <a href="/" class="logo">LMS Portal</a>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/support/">Support</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main class="container">
        <h1>Support Admin Panel</h1>
        
        <?php if (!$is_admin): ?>
            <div class="login-form">
                <h2>Admin Login</h2>
                <?php if (isset($error)): ?>
                    <div class="error"><?php echo htmlspecialchars($error); ?></div>
                <?php endif; ?>
                <form method="post">
                    <input type="hidden" name="login" value="1">
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
            </div>
        <?php else: ?>
            <div class="admin-panel">
                <p>Logged in as admin. Session: <?php echo htmlspecialchars(substr($admin_cookie, 0, 20)); ?>...</p>
                
                <h2>All Tickets</h2>
                <table class="tickets-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Subject</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($tickets as $ticket): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($ticket['id']); ?></td>
                            <td>
                                <a href="ticket.php?id=<?php echo $ticket['id']; ?>">
                                    <?php echo htmlspecialchars($ticket['subject']); ?>
                                </a>
                                <span class="meta">· <a href="ticket.php?id=<?php echo $ticket['id']; ?>&format=md">Preview</a></span>
                            </td>
                            <td><?php echo htmlspecialchars($ticket['status']); ?></td>
                            <td><?php echo htmlspecialchars($ticket['created_at']); ?></td>
                            <td>
                                <a href="?action=close&ticket_id=<?php echo $ticket['id']; ?>">Close</a>
                                <a href="?action=view&ticket_id=<?php echo $ticket['id']; ?>">View</a>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                
            </div>
        <?php endif; ?>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 LMS Portal. Educational Lab Environment.</p>
        </div>
    </footer>
</body>
</html>
