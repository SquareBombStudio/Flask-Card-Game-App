
RemindMe Hybrid (Flask + PHP + MySQL) - Upgraded with difficulty, timer, password rules

Structure:
- app.py (Flask handles auth, pages, deck generation)
- php/save_score.php (php endpoint to save score; allow CORS)
- php/get_leaderboard.php (php endpoint to fetch leaderboard by difficulty)
- database/remindme.sql (schema + test user)
- templates/* (HTML templates)
- static/js/game.js (game logic: timer starts on first flip, stops at end)
- static/img/cards/ (sample icons)

Quick setup:
1) Import database/remindme.sql into MySQL (phpMyAdmin or CLI).
   Test user: username=test password=test (bcrypt)
2) Copy php/ folder into your Apache htdocs/remindme/php/
3) Start Apache & MySQL
4) Install Python deps and run Flask app:
   pip install -r requirements.txt
   python app.py
5) Open http://127.0.0.1:5000, register/login, go to dashboard, choose difficulty, play, save score.

Notes:
 - Update DB credentials in app.py if needed.
 - save_score.php allows CORS from any origin. Adjust in production.
 - Leaderboards shown per difficulty on dashboard; also available via Flask API /leaderboard_data/<difficulty>.
