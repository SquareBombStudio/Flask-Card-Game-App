<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

$servername = "localhost";
$username = "root";
$password = "";
$dbname = "remindme_db";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
  http_response_code(500);
  echo json_encode(["error"=>"DB connection failed"]);
  exit;
}

$user_id = isset($_POST['user_id']) ? intval($_POST['user_id']) : 0;
$score = isset($_POST['score']) ? intval($_POST['score']) : 0;
$duree = isset($_POST['duree']) ? intval($_POST['duree']) : 0;
$difficulty = isset($_POST['difficulty']) ? $_POST['difficulty'] : 'medium';

if ($user_id <= 0) { echo json_encode(['error'=>'Invalid user']); exit; }

$stmt = $conn->prepare("INSERT INTO scores (user_id, score, duree, difficulty) VALUES (?, ?, ?, ?)");
$stmt->bind_param("iiis", $user_id, $score, $duree, $difficulty);
if ($stmt->execute()) {
  echo json_encode(['ok'=>'saved']);
} else {
  http_response_code(500);
  echo json_encode(['error'=>$conn->error]);
}
$stmt->close();
$conn->close();
?>