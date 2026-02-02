<?php
/**
 * Get More API Endpoint
 * "Get More" button के लिए - अगला batch extract करता है।
 * 
 * POST Request:
 * {
 *   "session_id": "abc123",
 *   "batch_size": 20
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "new_count": 20,
 *   "total_count": 40,
 *   "has_more": true,
 *   "data": [...]
 * }
 */

// CORS headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Allow long execution for scraping
set_time_limit(600); // 10 minutes

// Only POST allowed
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Include utils
require_once __DIR__ . '/../utils/response.php';

// Get JSON input
$input = json_decode(file_get_contents('php://input'), true);

// Validate session_id
if (empty($input['session_id'])) {
    Response::error('Session ID is required');
}

$session_id = preg_replace('/[^a-f0-9]/', '', $input['session_id']);
$batch_size = isset($input['batch_size']) ? intval($input['batch_size']) : 20;

// Limit batch size
if ($batch_size < 1) $batch_size = 10;
if ($batch_size > 50) $batch_size = 50;

// Load session file
$session_dir = realpath(__DIR__ . '/../../../data') . '/sessions';
$session_file = $session_dir . '/' . $session_id . '.json';

if (!file_exists($session_file)) {
    Response::error('Session not found', ['session_id' => $session_id]);
}

$session = json_decode(file_get_contents($session_file), true);
if (!$session) {
    Response::error('Invalid session data');
}

// Python script path
$python_dir = realpath(__DIR__ . '/../../python');
$python_script = $python_dir . '/main.py';

// Build command with offset (skip already extracted)
$keyword = escapeshellarg($session['keyword']);
$location = escapeshellarg($session['location']);
$country = escapeshellarg($session['country'] ?? 'India');
$offset = $session['total_extracted'];

// We'll use scroll-times to load more results, then skip first N
$scroll_times = ceil($offset / 10) + 5; // Extra scrolls to get past existing

// Build command with PYTHONPATH including user's local packages
$pythonpath = '/home/ubuntu_16gb/.local/lib/python3.10/site-packages:/usr/lib/python3/dist-packages:/usr/local/lib/python3.10/dist-packages';
$cmd = sprintf(
    'cd %s && PYTHONPATH=%s python3 main.py --keyword %s --location %s --country %s --limit %d --details --headless --scroll-times %d 2>&1',
    escapeshellarg($python_dir),
    escapeshellarg($pythonpath),
    $keyword,
    $location,
    $country,
    $offset + $batch_size + 10, // Get extra to account for duplicates
    $scroll_times
);

// Execute Python script
$output = shell_exec($cmd);

// Log the command and output for debugging
error_log("[GETMORE] Command: " . $cmd);
error_log("[GETMORE] Output length: " . strlen($output));
error_log("[GETMORE] First 500 chars: " . substr($output, 0, 500));

// Parse JSON from output
$json_start = strpos($output, '{');
$json_end = strrpos($output, '}');

if ($json_start === false || $json_end === false) {
    error_log("[GETMORE ERROR] Failed to find JSON in output. Full output: " . $output);
    Response::error('Python script failed - no valid JSON found', [
        'raw_output' => substr($output, 0, 1000),
        'command' => $cmd
    ]);
}

$json_str = substr($output, $json_start, $json_end - $json_start + 1);
$result = json_decode($json_str, true);

if ($result === null) {
    error_log("[GETMORE ERROR] JSON decode failed. JSON string: " . $json_str);
    error_log("[GETMORE ERROR] JSON error: " . json_last_error_msg());
    Response::error('Invalid JSON from Python', [
        'json_error' => json_last_error_msg(),
        'json_snippet' => substr($json_str, 0, 500)
    ]);
}

if (!isset($result['success']) || !$result['success']) {
    error_log("[GETMORE ERROR] Python script returned error: " . ($result['error'] ?? 'Unknown'));
    Response::error($result['error'] ?? 'Unknown Python error', [
        'python_result' => $result
    ]);
}

$all_data = $result['data'] ?? [];

// Filter out already seen records using hash
$seen_hashes = $session['seen_hashes'] ?? [];
$new_data = [];

foreach ($all_data as $item) {
    $hash = md5(($item['name'] ?? '') . ($item['address'] ?? ''));
    if (!in_array($hash, $seen_hashes)) {
        $new_data[] = $item;
        $seen_hashes[] = $hash;
        
        if (count($new_data) >= $batch_size) {
            break;
        }
    }
}

// Update session
$session['last_card'] = !empty($new_data) ? [
    'name' => end($new_data)['name'] ?? '',
    'place_id' => end($new_data)['place_id'] ?? '',
    'index' => $session['total_extracted'] + count($new_data)
] : $session['last_card'];

$session['total_extracted'] += count($new_data);
$session['batches_completed']++;
$session['seen_hashes'] = $seen_hashes;
$session['all_data'] = array_merge($session['all_data'], $new_data);
$session['updated_at'] = date('Y-m-d H:i:s');

// Save updated session
file_put_contents($session_file, json_encode($session, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

// Determine if there's more data
$has_more = count($new_data) >= $batch_size;

// Response
echo json_encode([
    'success' => true,
    'session_id' => $session_id,
    'new_count' => count($new_data),
    'total_count' => $session['total_extracted'],
    'batches_completed' => $session['batches_completed'],
    'has_more' => $has_more,
    'data' => $new_data,
    'timestamp' => date('Y-m-d H:i:s')
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
