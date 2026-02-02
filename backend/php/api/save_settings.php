<?php
/**
 * Save Settings API Endpoint
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

require_once __DIR__ . '/../utils/response.php';

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    Response::error('Invalid JSON input');
}

$data_dir = realpath(__DIR__ . '/../../../data');
$settings_file = $data_dir . '/settings.json';

// Merge with existing
$current_settings = [];
if (file_exists($settings_file)) {
    $current_settings = json_decode(file_get_contents($settings_file), true) ?? [];
}

$new_settings = array_merge($current_settings, $input);

if (file_put_contents($settings_file, json_encode($new_settings, JSON_PRETTY_PRINT))) {
    echo json_encode(['success' => true, 'message' => 'Settings saved successfully']);
} else {
    Response::error('Failed to save settings file');
}
