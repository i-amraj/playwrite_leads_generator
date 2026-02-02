<?php

class Response {
    public static function json($success, $message, $data = null) {
        header('Content-Type: application/json');
        echo json_encode([
            'success' => $success,
            'message' => $message,
            'data' => $data
        ]);
        exit;
    }

    public static function success($message, $data = null) {
        self::json(true, $message, $data);
    }

    public static function error($message, $data = null) {
        self::json(false, $message, $data);
    }
}
