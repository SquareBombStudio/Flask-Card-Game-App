
import os, random, re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, url_for as flask_url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('REMINDME_SECRET','80db887ecdef3a36fed40a4c3995eaf8f05a61769a5d18329a6025621842e6fb')

# DB config (change to your credentials)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "remindme_db"
}

import mysql.connector
import bcrypt as _bcrypt

def get_db_conn():
    return mysql.connector.connect(**DB_CONFIG)

# Helper: list random icons based on difficulty (pairs)
def get_deck_for_difficulty(difficulty):
    folder = os.path.join(app.static_folder, 'img/cards')
    icons = [f for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg','.jpeg','.svg'))]
    pairs_count = {'easy':6, 'medium':8, 'hard':12}.get(difficulty,8)
    if pairs_count > len(icons):
        pairs_count = min(len(icons), pairs_count)
    selected = random.sample(icons, pairs_count)
    deck = selected * 2
    random.shuffle(deck)
    return [flask_url_for('static', filename='img/cards/'+p) for p in deck]

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        # basic server-side password policy
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r'[^A-Za-z0-9]', password):
            error = "Mot de passe trop faible (min 8, 1 majuscule, 1 chiffre, 1 caractère spécial)."
        else:
            hashed = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
            conn = get_db_conn()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
                conn.commit()
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                error = "Nom d'utilisateur déjà pris."
            finally:
                cursor.close(); conn.close()
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close(); conn.close()
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
    difficulty = request.args.get('difficulty','medium')
    deck = get_deck_for_difficulty(difficulty)
    return render_template('game.html', username=session.get('username'), user_id=session.get('user_id'), deck=deck, difficulty=difficulty)

@app.route('/leaderboard_data/<difficulty>')
def leaderboard_data(difficulty):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT u.username, MIN(s.duree) AS best_time,
               (SELECT score FROM scores WHERE user_id = u.id AND difficulty=%s ORDER BY duree ASC, score ASC LIMIT 1) AS best_moves
        FROM users u JOIN scores s ON s.user_id = u.id
        WHERE s.difficulty=%s
        GROUP BY u.id
        ORDER BY best_time ASC, best_moves ASC
        LIMIT 20
    """
    cursor.execute(query, (difficulty, difficulty))
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True)
