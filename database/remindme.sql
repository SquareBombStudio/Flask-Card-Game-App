
CREATE DATABASE IF NOT EXISTS remindme_db;
USE remindme_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  score INT NOT NULL,
  duree INT NOT NULL,
  difficulty ENUM('easy','medium','hard') NOT NULL DEFAULT 'medium',
  date_jeu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Test user: username test / password test (bcrypt hash)
INSERT IGNORE INTO users (username, password) VALUES ('test', '$2b$12$KIXQJm8DvR6r0p5U2eYV7u5Z8gJfJ3r6cQZx0GQq9mE1O7hG8vH2');
