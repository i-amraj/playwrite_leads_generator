<?php
/**
 * Get Settings API Endpoint
 */

header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

$data_dir = realpath(__DIR__ . '/../../../data');
$settings_file = $data_dir . '/settings.json';

$settings = [];

if (file_exists($settings_file)) {
    $settings = json_decode(file_get_contents($settings_file), true);
}

// Default settings if empty
if (empty($settings)) {
    $settings = [
        'theme' => 'light',
        'notifications' => true,
        'export_format' => 'xlsx',
        'auto_scroll' => true
    ];
}

echo json_encode(['success' => true, 'data' => $settings]);
