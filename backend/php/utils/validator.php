<?php

class Validator {
    public static function validateSearchRequest($postData) {
        if (empty($postData['keyword'])) {
            return "Keyword is required";
        }
        if (empty($postData['location'])) {
            return "Location is required";
        }
        return null; // No error
    }
}
