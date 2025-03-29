<?php
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

$clients = [];
$messages = [];
$messageHistoryFile = __DIR__ . '/message_history.json';

// Tải lịch sử tin nhắn từ file JSON
function loadMessageHistory() {
    global $messageHistoryFile;
    if (file_exists($messageHistoryFile)) {
        $content = file_get_contents($messageHistoryFile);
        return $content ? json_decode($content, true) : [];
    }
    return [];
}

// Lưu lịch sử tin nhắn vào file JSON
function saveMessageHistory() {
    global $messages, $messageHistoryFile;
    file_put_contents($messageHistoryFile, json_encode($messages, JSON_PRETTY_PRINT));
}

// Tải lịch sử tin nhắn khi khởi động server
$messages = loadMessageHistory();

// Xử lý các route
$requestMethod = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($path === '/devices' && $requestMethod === 'GET') {
    // API để liệt kê các thiết bị đã kết nối
    echo json_encode(array_keys($clients));
} elseif ($path === '/send_message' && $requestMethod === 'POST') {
    // API để nhận và phát tin nhắn
    $data = json_decode(file_get_contents('php://input'), true);
    $senderId = $data['sender_id'] ?? null;
    $message = $data['message'] ?? null;

    if ($senderId && $message) {
        $timestamp = date('Y-m-d H:i:s');
        $newMessage = ['sender_id' => $senderId, 'message' => $message, 'timestamp' => $timestamp];
        $messages[] = $newMessage;
        saveMessageHistory();
        echo json_encode(["status" => "Message sent"]);
    } else {
        http_response_code(400);
        echo json_encode(["status" => "Invalid data"]);
    }
} elseif ($path === '/messages' && $requestMethod === 'GET') {
    // API để lấy danh sách tin nhắn
    echo json_encode(array_slice($messages, -50));
} elseif ($path === '/send_file' && $requestMethod === 'POST') {
    // API để nhận và lưu trữ file dưới dạng Base64
    $data = json_decode(file_get_contents('php://input'), true);
    $senderId = $data['sender_id'] ?? null;
    $fileName = $data['file_name'] ?? null;
    $fileData = $data['file_data'] ?? null;

    if ($senderId && $fileName && $fileData) {
        $timestamp = date('Y-m-d H:i:s');
        $newMessage = ['sender_id' => $senderId, 'file_name' => $fileName, 'file_data' => $fileData, 'timestamp' => $timestamp];
        $messages[] = $newMessage;
        saveMessageHistory();
        echo json_encode(["status" => "File saved"]);
    } else {
        http_response_code(400);
        echo json_encode(["status" => "Invalid data"]);
    }
} else {
    http_response_code(404);
    echo json_encode(["status" => "Not found"]);
}
?>
