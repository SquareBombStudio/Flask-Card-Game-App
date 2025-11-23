
RemindMe website app game (Flask + HTML + CSS(Bootstrap) + JavaScript + MySQL)

Structure:
- app.py (Flask handles auth, pages, deck generation)
- database/remindmedb.sql (schema + test user)
- templates/* (HTML templates)
- static/js/game.js (game logic: timer starts on first flip, stops at end)
- static/img/cards/ (game icons)

Quick setup:
1) Import database/remindmedb.sql into MySQL (phpMyAdmin or CLI).
   Test user: username=test password=test (bcrypt)
3) Start Apache & MySQL
3) Create Virtual enviroment :
   python -m venv venv 
4) Install Python deps and run Flask app:
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
5) Open http://127.0.0.1:5000, register/login, go to dashboard, choose difficulty, play, save score.

Notes:
 - Update DB credentials in app.py if needed.
 - Leaderboards shown per difficulty on dashboard available via Flask API /leaderboard_data/<difficulty>.
