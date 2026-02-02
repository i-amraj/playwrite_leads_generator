<?php
/**
 * Status API Endpoint
 * Session का current status return करता है।
 * 
 * POST Request:
 * {
 *   "session_id": "abc123"
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "session_id": "abc123",
 *   "total_extracted": 40,
 *   "batches_completed": 2,
 *   "query": "gym in lucknow"
 * }
 */

// CORS headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Get session_id from POST or GET
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $session_id = $input['session_id'] ?? '';
} else {
    $session_id = $_GET['session_id'] ?? '';
}

// Validate
if (empty($session_id)) {
    echo json_encode(['success' => false, 'error' => 'Session ID is required']);
    exit;
}

$session_id = preg_replace('/[^a-f0-9]/', '', $session_id);

// Load session file
$session_dir = realpath(__DIR__ . '/../../../data') . '/sessions';
$session_file = $session_dir . '/' . $session_id . '.json';

if (!file_exists($session_file)) {
    echo json_encode(['success' => false, 'error' => 'Session not found']);
    exit;
}

$session = json_decode(file_get_contents($session_file), true);

// Response (without all_data to keep it light)
echo json_encode([
    'success' => true,
    'session_id' => $session_id,
    'query' => $session['query'] ?? '',
    'keyword' => $session['keyword'] ?? '',
    'location' => $session['location'] ?? '',
    'total_extracted' => $session['total_extracted'] ?? 0,
    'batches_completed' => $session['batches_completed'] ?? 0,
    'created_at' => $session['created_at'] ?? '',
    'updated_at' => $session['updated_at'] ?? '',
    'last_card' => $session['last_card'] ?? null
], JSON_PRETTY_PRINT);
