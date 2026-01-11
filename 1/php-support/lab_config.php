<?php
function load_env_file(string $path, array $config): array {
    if (!file_exists($path)) {
        return $config;
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return $config;
    }

    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || strpos($line, '#') === 0) {
            continue;
        }
        $parts = explode('=', $line, 2);
        if (count($parts) === 2) {
            $config[trim($parts[0])] = trim($parts[1]);
        }
    }

    return $config;
}

function load_lab_config(): array {
    $config_path = __DIR__ . '/../config/lab.env';
    $credentials_path = __DIR__ . '/../config/credentials.env';
    $config = [
        'LAB_DIFFICULTY' => 'hard',
        'RSC_TOKEN' => 'lms-integration-token',
        'PHP_ADMIN_PASSWORD_HASH' => ''
    ];

    $config = load_env_file($config_path, $config);
    $config = load_env_file($credentials_path, $config);

    return $config;
}

$LAB_CONFIG = load_lab_config();
$LAB_DIFFICULTY = strtolower($LAB_CONFIG['LAB_DIFFICULTY'] ?? 'hard');
?>
