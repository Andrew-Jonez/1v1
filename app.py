import re
from flask import Flask, render_template, request, session, jsonify
import random
import os
#from dotenv import load_dotenv
#import sqlite3
import time
import pyodbc

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')

MAX_SCORE = 21

def score2points():
    return random.randint(0, 1)

def rebound():
    return random.choice(["You got the ball back!", "Your Opponent rebounded the ball!"])

def opponent_offense():
    return random.choice(["Your opponent dribbled the ball!", "Your Opponent shot the ball!"])

def steal_ball():
    steal_chance = 8
    return random.randint(0, 10) > steal_chance

def init_db():
    try:
        with get_sql_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT * FROM sysobjects WHERE name='leaderboard' AND xtype='U'
                )
                CREATE TABLE leaderboard (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    player_name NVARCHAR(50) NOT NULL,
                    time_seconds FLOAT NOT NULL
                )
            """)
            conn.commit()
    except Exception as e:
        print("Error initializing database:", e)

def get_sql_connection():
    return pyodbc.connect(
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={os.environ['SQL_SERVER_NAME']}.database.windows.net;"
        f"Database=1v1-db;"
        f"Uid=sqladminuser;"
        f"Pwd={os.environ['SQL_ADMIN_PASSWORD']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )


def save_score(name, seconds):
    try:
        with get_sql_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO leaderboard (player_name, time_seconds) VALUES (?, ?)",
                (name, seconds)
            )
            conn.commit()
    except Exception as e:
        print("Error saving score:", e)


@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    name = data.get('name', '').strip()

    if not re.match(r'^[\w \-]{1,20}$', name):
        return jsonify({'error': 'Invalid name'}), 400

    session['player_name'] = name
    session['start_time'] = time.time()
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    session['my_score'] = 0
    session['opponent_score'] = 0
    session['turn'] = "player_turn"
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    data = request.get_json()
    action_type = data.get('action')
    steal_attempt = data.get('steal', False)

    my_score = session.get('my_score', 0)
    opponent_score = session.get('opponent_score', 0)
    turn = session.get('turn', 'player_turn')
    messages = []
    auto_continue = False

    if turn == 'awaiting_steal':
        if steal_attempt:
            if steal_ball():
                messages.append("You stole the ball!")
                session['turn'] = 'player_turn'
            else:
                messages.append("Steal failed.")
                session['turn'] = 'opponent_turn'
                auto_continue = True
        else:
            messages.append("You must attempt a steal!")
        return jsonify({
            'messages': messages,
            'my_score': my_score,
            'opponent_score': opponent_score,
            'game_over': False,
            'auto_continue': auto_continue
        })


    if turn == 'player_turn':
        if action_type == 'shoot':
            if score2points():
                my_score += 2
                messages.append("You scored 2 points!")
                session['turn'] = 'player_turn'
            else:
                messages.append("You missed the shot.")
                rebound_result = rebound()
                messages.append(rebound_result)
                if rebound_result == "Your Opponent rebounded the ball!":
                    session['turn'] = 'opponent_turn'
                    auto_continue = True
                else:
                    session['turn'] = 'player_turn'

        elif action_type == 'dribble':
            messages.append("You dribbled the ball.")
            session['turn'] = 'player_turn'

    elif turn == 'opponent_turn':
        if action_type == 'auto' or action_type is None:
            offense_result = opponent_offense()
            messages.append(offense_result)

            if offense_result == "Your opponent dribbled the ball!":
                messages.append("Press 'Steal' to try to take the ball.")
                session['turn'] = 'awaiting_steal'
                auto_continue = False
            elif offense_result == "Your Opponent shot the ball!":
                if score2points():
                    opponent_score += 2
                    messages.append("Your opponent scored 2 points!")
                    session['turn'] = 'opponent_turn'
                    auto_continue = True
                else:
                    messages.append("Your opponent missed.")
                    rebound_result = rebound()
                    messages.append(rebound_result)
                    if rebound_result == "Your Opponent rebounded the ball!":
                        session['turn'] = 'opponent_turn'
                        auto_continue = True
                    else:
                        session['turn'] = 'player_turn'
                        auto_continue = False

    # Update scores
    session['my_score'] = my_score
    session['opponent_score'] = opponent_score

    # Game over logic
    if my_score >= MAX_SCORE:
        end_time = time.time()
        start_time = session.get('start_time', end_time)
        total_time = end_time - start_time
        save_score(session.get('player_name', 'Unknown'), total_time)
        messages.append(f"You won! Final Score: {my_score} - {opponent_score}")
    elif opponent_score >= MAX_SCORE:
        messages.append(f"You lost. Final Score: {my_score} - {opponent_score}")

    return jsonify({
        'messages': messages,
        'my_score': my_score,
        'opponent_score': opponent_score,
        'game_over': my_score >= MAX_SCORE or opponent_score >= MAX_SCORE,
        'auto_continue': auto_continue
    })

@app.route('/leaderboard')
def leaderboard():
    try:
        with get_sql_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 10 player_name, time_seconds
                FROM leaderboard
                ORDER BY time_seconds ASC
            """)
            top_scores = cursor.fetchall()

        return jsonify([
            {'name': row[0], 'time': round(row[1], 2)}
            for row in top_scores
        ])
    except Exception as e:
        print("Error fetching leaderboard:", e)
        return jsonify([]), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True)