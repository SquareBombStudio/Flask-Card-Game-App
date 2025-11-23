import os
import random
import re
from flask import (
    Flask, render_template, request, redirect, url_for, session, jsonify,
    url_for as flask_url_for
)
import pymysql
import bcrypt as _bcrypt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('REMINDME_SECRET', 'replace_with_a_real_random_secret')


DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",              
    "password": "",         
    "database": "remindme_db", 
    "cursorclass": pymysql.cursors.DictCursor,
    "charset": "utf8mb4",
    "connect_timeout": 10,
    "read_timeout": 10,
    "write_timeout": 10,
}

def get_db_conn():
    return pymysql.connect(**DB_CONFIG)


# Helper: list random icons based on difficulty (pairs)
def get_deck_for_difficulty(difficulty):
    folder = os.path.join(app.static_folder, 'img/cards')
    icons = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))]
    pairs_count = {'easy': 6, 'medium': 8, 'hard': 12}.get(difficulty, 8)
    pairs_count = min(len(icons), pairs_count)
    selected = random.sample(icons, pairs_count)
    deck = selected * 2
    random.shuffle(deck)
    return [flask_url_for('static', filename='img/cards/' + p) for p in deck]


# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r'[^A-Za-z0-9]', password):
            error = "Mot de passe trop faible (min 8, 1 majuscule, 1 chiffre, 1 caractère spécial)."
        else:
            hashed = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
            conn = get_db_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
                conn.commit()
                return redirect(url_for('login'))
            except pymysql.err.IntegrityError:
                error = "Nom d'utilisateur déjà pris."
            finally:
                conn.close()
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
                user = cur.fetchone()
        finally:
            conn.close()

        if user and _bcrypt.checkpw(password.encode(), user['password'].encode()):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            error = "Identifiants incorrects."
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/game')
def game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    difficulty = request.args.get('difficulty', 'medium')
    deck = get_deck_for_difficulty(difficulty)
    return render_template('game.html', username=session.get('username'), user_id=session.get('user_id'), deck=deck, difficulty=difficulty)


# Save score endpoint
@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_id = int(data.get("user_id", 0))
    score = int(data.get("score", 0))
    duree = int(data.get("duree", 0))
    difficulty = data.get("difficulty", "medium")

    if user_id <= 0:
        return jsonify({"error": "Invalid user"}), 400

    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO scores (user_id, score, duree, difficulty) VALUES (%s, %s, %s, %s)",
                        (user_id, score, duree, difficulty))
        conn.commit()
    finally:
        conn.close()

    return jsonify({"ok": True})


# Leaderboard (per difficulty)
@app.route('/leaderboard_data/<difficulty>')
def leaderboard_data(difficulty):
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT u.username,
                       MIN(s.duree) AS best_time,
                       (
                           SELECT s2.score
                           FROM scores s2
                           WHERE s2.user_id = u.id AND s2.difficulty = %s
                           ORDER BY s2.duree ASC, s2.score ASC
                           LIMIT 1
                       ) AS best_moves
                FROM users u
                JOIN scores s ON s.user_id = u.id
                WHERE s.difficulty = %s
                GROUP BY u.id
                ORDER BY best_time ASC, best_moves ASC
                LIMIT 20
            """
            cur.execute(sql, (difficulty, difficulty))
            rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True)
