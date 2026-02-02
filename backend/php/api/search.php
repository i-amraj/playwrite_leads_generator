<?php
/**
 * Search API Endpoint
 * Frontend से search request लेता है और Python scraper को call करता है।
 * 
 * POST Request:
 * {
 *   "keyword": "gym",
 *   "location": "lucknow",
 *   "country": "india",
 *   "limit": 20
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "session_id": "abc123",
 *   "total_found": 45,
 *   "extracted": 20,
 *   "has_more": true,
 *   "data": [...]
 * }
 */

// CORS headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// Increase time limit for long scrolling
set_time_limit(600); // 10 minutes

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only POST allowed
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Include utils
require_once __DIR__ . '/../utils/response.php';
require_once __DIR__ . '/../utils/validator.php';

// Get JSON input
$input = json_decode(file_get_contents('php://input'), true);

// Validate input
$error = Validator::validateSearchRequest($input);
if ($error) {
    Response::error($error);
}

// Extract parameters
$keyword = escapeshellarg(trim($input['keyword']));
$location = escapeshellarg(trim($input['location']));
$country = isset($input['country']) ? escapeshellarg(trim($input['country'])) : "'india'";
$limit = isset($input['limit']) ? intval($input['limit']) : 20;

$sales_person = isset($input['sales_person']) ? trim($input['sales_person']) : '';
$sales_team = isset($input['sales_team']) ? trim($input['sales_team']) : '';

// Limit validation
if ($limit < 1) $limit = 10;
if ($limit > 50) $limit = 50; // Max 50 per request

// Generate deterministic session ID based on criteria
$criteria_string = strtolower(trim($input['keyword']) . '|' . trim($input['location']) . '|' . trim($input['country'] ?? 'india'));
$session_id = md5($criteria_string);

// Build search query
$query = trim($input['keyword']) . ' in ' . trim($input['location']);

// Check for existing session cache
$session_dir = realpath(__DIR__ . '/../../../data') . '/sessions';
if (!is_dir($session_dir)) {
    mkdir($session_dir, 0755, true);
}
$session_file = $session_dir . '/' . $session_id . '.json';

// If session exists, return cached data immediately
if (file_exists($session_file)) {
    $session_data = json_decode(file_get_contents($session_file), true);
    
    // Check if it's valid
    if ($session_data && isset($session_data['all_data'])) {
        // Return cached response
        echo json_encode([
            'success' => true,
            'session_id' => $session_id,
            'query' => $query,
            'total_found' => $session_data['total_found_approx'] ?? count($session_data['all_data']), # Fallback if specific total logic varies
            'extracted' => count($session_data['all_data']),
            'has_more' => true, // Assuming more might be available if user wants try
            'data' => $session_data['all_data'],
            'restored' => true, // Flag for specific UI handling
            'timestamp' => date('Y-m-d H:i:s')
        ], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
        exit;
    }
}

// Python script path
$python_dir = realpath(__DIR__ . '/../../python');
$python_script = $python_dir . '/main.py';

// Check if Python script exists
if (!file_exists($python_script)) {
    Response::error('Python scraper not found', ['path' => $python_script]);
}

    // Build and execute Python command
    // Set PYTHONPATH to include user's local packages and system packages
    $pythonpath = '/home/ubuntu_16gb/.local/lib/python3.10/site-packages:/usr/lib/python3/dist-packages:/usr/local/lib/python3.10/dist-packages';
    $cmd = sprintf(
        'cd %s && PYTHONPATH=%s python3 main.py --keyword %s --location %s --country %s --limit %d --details --headless 2>&1',
        escapeshellarg($python_dir),
        escapeshellarg($pythonpath),
        escapeshellarg($keyword),
        escapeshellarg($location),
        escapeshellarg($country),
        $limit
    );

// Execute Python script
$output = shell_exec($cmd);

// Try to parse JSON from output
$json_start = strpos($output, '{');
$json_end = strrpos($output, '}');

if ($json_start === false || $json_end === false) {
    Response::error('Python script failed', ['raw_output' => substr($output, 0, 500)]);
}

$json_str = substr($output, $json_start, $json_end - $json_start + 1);
$result = json_decode($json_str, true);

if ($result === null) {
    Response::error('Invalid JSON from Python', ['raw' => substr($json_str, 0, 500)]);
}

// Check Python result
if (!isset($result['success']) || !$result['success']) {
    Response::error($result['error'] ?? 'Unknown Python error');
}

$data = $result['data'] ?? [];
$total_found_approx = $result['total_found'] ?? count($data);

// Save session for "Get More" functionality
$session_data = [
    'session_id' => $session_id,
    'query' => $query,
    'keyword' => trim($input['keyword']),
    'location' => trim($input['location']),
    'country' => trim($input['country'] ?? 'india'),
    'sales_person' => $sales_person,
    'sales_team' => $sales_team,
    'created_at' => date('Y-m-d H:i:s'),
    'last_card' => !empty($data) ? [
        'name' => end($data)['name'] ?? '',
        'place_id' => end($data)['place_id'] ?? '',
        'index' => count($data)
    ] : null,
    'total_extracted' => count($data),
    'total_found_approx' => $total_found_approx, // Save detected total
    'batches_completed' => 1,
    'seen_hashes' => array_map(function($item) {
        return md5(($item['name'] ?? '') . ($item['address'] ?? ''));
    }, $data),
    'all_data' => $data
];

file_put_contents($session_file, json_encode($session_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

// Response
echo json_encode([
    'success' => true,
    'session_id' => $session_id,
    'query' => $query,
    'total_found' => $total_found_approx,
    'extracted' => count($data),
    'has_more' => count($data) >= $limit,
    'data' => $data,
    'timestamp' => date('Y-m-d H:i:s')
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
