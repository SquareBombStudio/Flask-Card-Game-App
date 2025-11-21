<?php
header("Access-Control-Allow-Origin: *");
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "remindme_db";
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) { echo json_encode([]); exit; }
$difficulty = isset($_GET['difficulty']) ? $_GET['difficulty'] : 'medium';
$sql = "SELECT u.username, MIN(s.duree) AS best_time, (SELECT score FROM scores WHERE user_id = u.id AND difficulty=? ORDER BY duree ASC, score ASC LIMIT 1) AS best_moves
        FROM users u JOIN scores s ON s.user_id = u.id WHERE s.difficulty=? GROUP BY u.id ORDER BY best_time ASC, best_moves ASC LIMIT 20";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ss", $difficulty, $difficulty);
$stmt->execute();
$res = $stmt->get_result();
$rows = array();
while($r = $res->fetch_assoc()) $rows[] = $r;
echo json_encode($rows);
$conn->close();
?>