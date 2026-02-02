<?php
/**
 * Get History API Endpoint
 * Scans data/sessions directory to return past search sessions
 */

// Headers
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

require_once __DIR__ . '/../utils/response.php';

$session_dir = realpath(__DIR__ . '/../../../data/sessions');

if (!is_dir($session_dir)) {
    echo json_encode(['success' => true, 'data' => []]);
    exit;
}

$files = glob($session_dir . '/*.json');
$history = [];

foreach ($files as $file) {
    $content = file_get_contents($file);
    if ($content) {
        $data = json_decode($content, true);
        if ($data) {
            // Summary only
            $history[] = [
                'session_id' => $data['session_id'],
                'keyword' => $data['keyword'] ?? 'Unknown',
                'location' => $data['location'] ?? 'Unknown',
                'country' => $data['country'] ?? 'India',
                'date' => $data['created_at'] ?? date('Y-m-d H:i:s', filemtime($file)),
                'total_leads' => $data['total_extracted'] ?? 0,
                'status' => 'Completed' // Assuming completed if file exists, logic can be enhanced
            ];
        }
    }
}

// Sort by date desc
usort($history, function($a, $b) {
    return strtotime($b['date']) - strtotime($a['date']);
});

echo json_encode(['success' => true, 'data' => $history]);
