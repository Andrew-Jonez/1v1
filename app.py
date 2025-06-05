from flask import Flask, render_template, request, session, jsonify
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key'

MAX_SCORE = 21

def score2points():
    return random.randint(0, 1)

def rebound():
    return random.choice(["You got the ball back!", "Your Opponent rebounded the ball!"])

def opponent_offense():
    return random.choice(["Your opponent passed the ball!", "Your Opponent shot the ball!"])

def steal_ball():
    steal_chance = 8
    return random.randint(0, 10) > steal_chance

@app.route('/')
def index():
    session['my_score'] = 0
    session['opponent_score'] = 0
    session['turn'] = "player_turn"
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    action_type = request.json['action']
    steal_attempt = request.json.get('steal', False)

    my_score = session.get('my_score', 0)
    opponent_score = session.get('opponent_score', 0)
    turn = session.get('turn', 'player_turn')
    messages = []
    prompt_steal = False

    if my_score >= MAX_SCORE or opponent_score >= MAX_SCORE:
        messages.append("Game is over.")
        return jsonify({
            'messages': messages,
            'my_score': my_score,
            'opponent_score': opponent_score,
            'game_over': True
        })

    if turn == 'awaiting_steal' and steal_attempt:
        if steal_ball():
            messages.append("You stole the ball!")
            session['turn'] = 'player_turn'
        else:
            messages.append("Steal failed.")
            session['turn'] = 'opponent_turn'
        return jsonify({
            'messages': messages,
            'my_score': my_score,
            'opponent_score': opponent_score,
            'game_over': False
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
                else:
                    session['turn'] = 'player_turn'

        elif action_type == 'pass':
            messages.append("You passed the ball.")
            session['turn'] = 'player_turn'

    elif turn == 'opponent_turn':
        offense_result = opponent_offense()
        messages.append(offense_result)

        if offense_result == "Your opponent passed the ball!":
            messages.append("Press 'Steal' to try to take the ball.")
            session['turn'] = 'awaiting_steal'
            prompt_steal = True
            return jsonify({
                'messages': messages,
                'my_score': my_score,
                'opponent_score': opponent_score,
                'prompt_steal': prompt_steal,
                'game_over': False
            })
        else:
            if score2points():
                opponent_score += 2
                messages.append("Your opponent scored 2 points!")
                session['turn'] = 'opponent_turn'
            else:
                messages.append("Your opponent missed.")
                rebound_result = rebound()
                messages.append(rebound_result)
                if rebound_result == "Your Opponent rebounded the ball!":
                    session['turn'] = 'opponent_turn'
                else:
                    session['turn'] = 'player_turn'

    session['my_score'] = my_score
    session['opponent_score'] = opponent_score

    if my_score >= MAX_SCORE:
        messages.append(f"You won! Final Score: {my_score} - {opponent_score}")
    elif opponent_score >= MAX_SCORE:
        messages.append(f"You lost. Final Score: {my_score} - {opponent_score}")

    return jsonify({
        'messages': messages,
        'my_score': my_score,
        'opponent_score': opponent_score,
        'game_over': my_score >= MAX_SCORE or opponent_score >= MAX_SCORE
    })

if __name__ == '__main__':
    app.run(debug=True)
