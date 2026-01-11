<?php
require_once 'db.php';
require_once 'lab_config.php';

$message = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $subject = $_POST['subject'] ?? '';
    $ticket_message = $_POST['message'] ?? '';
    
    if (empty($subject) || empty($ticket_message)) {
        $error = 'Please fill in all fields';
    } else {
        $stmt = $db->prepare("INSERT INTO tickets (subject, message) VALUES (?, ?)");
        $stmt->bindValue(1, $subject, SQLITE3_TEXT);
        $stmt->bindValue(2, $ticket_message, SQLITE3_TEXT);
        
        if ($stmt->execute()) {
            $ticket_id = $db->lastInsertRowID();
            header("Location: ticket.php?id=$ticket_id");
            exit;
        } else {
            $error = 'Failed to create ticket';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Support Ticket</title>
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
                    <li><a href="/support/">Support</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main class="container">
        <h1>Create Support Ticket</h1>
        
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <form method="post" action="">
            <div class="form-group">
                <label for="subject">Subject:</label>
                <input type="text" id="subject" name="subject" required 
                       placeholder="Enter ticket subject">
            </div>
            
            <div class="form-group">
                <label for="message">Message:</label>
                <textarea id="message" name="message" rows="10" required 
                          placeholder="Describe your issue"></textarea>
            </div>
            
            <button type="submit">Submit Ticket</button>
        </form>
        
        <div class="info-box" style="margin-top: 20px;">
            <h3>Markdown Supported</h3>
            <p>You can format messages using basic Markdown for richer previews.</p>
            <p><strong>Examples:</strong> <code>**bold**</code>, <code># heading</code>, <code>[link](https://example.com)</code></p>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 LMS Portal. Educational Lab Environment.</p>
        </div>
    </footer>
</body>
</html>
