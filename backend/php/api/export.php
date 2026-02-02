<?php
/**
 * Export API Endpoint
 * Session data को Excel file में export करता है।
 * 
 * POST Request:
 * {
 *   "session_id": "abc123"
 * }
 * 
 * Response: Excel file download
 */

// CORS headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only POST allowed
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Get JSON input
$input = json_decode(file_get_contents('php://input'), true);

// Validate session_id
if (empty($input['session_id'])) {
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Session ID is required']);
    exit;
}

$session_id = preg_replace('/[^a-f0-9]/', '', $input['session_id']);

// Load session file
$session_dir = realpath(__DIR__ . '/../../../data') . '/sessions';
$session_file = $session_dir . '/' . $session_id . '.json';

if (!file_exists($session_file)) {
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Session not found']);
    exit;
}

$session = json_decode(file_get_contents($session_file), true);
if (!$session || empty($session['all_data'])) {
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'No data to export']);
    exit;
}

$data = $session['all_data'];

// Data needed for fields
$sales_person = $session['sales_person'] ?? '';
$sales_team = $session['sales_team'] ?? '';
$category = $session['keyword'] ?? ''; 
$city = $session['location'] ?? ''; 
$country = $session['country'] ?? 'India';

// Generate CSV headers
$filename = sprintf('%s_%s_%s.csv', $category, $city, date('Ymd_His'));
header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="' . $filename . '"');

$output = fopen('php://output', 'w');

// Add BOM
fprintf($output, chr(0xEF).chr(0xBB).chr(0xBF));

// Header row
// Template: Name,Phone,Email,City,Country,Salesperson,Sales Team,Category
fputcsv($output, [
    'Name',
    'Phone',
    'Email',
    'City',
    'Country',
    'Salesperson',
    'Sales Team',
    'Category'
]);

// Data rows
foreach ($data as $item) {
    // City extraction from address if possible, else fallback to session location
    // Address format often: "Area, City, State"
    // But keeping it simple for now -> Session Location is safest fallback
    
    // Email is usually not available on Maps, leave empty or check if scraper got it
    $email = $item['email'] ?? ''; 
    
    fputcsv($output, [
        $item['name'] ?? '',
        $item['phone'] ?? '',
        $email,
        $city,
        $country,
        $sales_person,
        $sales_team,
        $category
    ]);
}

fclose($output);
exit;
