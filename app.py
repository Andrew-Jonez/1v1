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
    session['turn'] = "player"
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    action_type = request.json['action']
    steal_attempt = request.json.get('steal', False)

    my_score = session.get('my_score', 0)
    opponent_score = session.get('opponent_score', 0)
    messages = []

    if my_score >= MAX_SCORE or opponent_score >= MAX_SCORE:
        messages.append("Game is over.")
        return jsonify({
            'messages': messages,
            'my_score': my_score,
            'opponent_score': opponent_score,
            'game_over': True
        })

    if action_type == 'shoot':
        if score2points():
            my_score += 2
            messages.append("You scored 2 points!")
        else:
            messages.append("You missed the shot.")
            rebound_result = rebound()
            messages.append(rebound_result)
            if rebound_result == "Your Opponent rebounded the ball!":
                offense_result = opponent_offense()
                messages.append(offense_result)
                if offense_result == "Your opponent passed the ball!":
                    if steal_attempt:
                        if steal_ball():
                            messages.append("You stole the ball!")
                        else:
                            messages.append("Steal failed.")
                    else:
                        messages.append("You let them pass.")
                else:
                    if score2points():
                        opponent_score += 2
                        messages.append("Your opponent scored 2 points!")
                    else:
                        messages.append("Your opponent missed.")
                        rebound_result = rebound()

    elif action_type == 'pass':
        messages.append("You passed the ball.")
        offense_result = opponent_offense()
        messages.append(offense_result)
        if offense_result == "Your opponent passed the ball!":
            if steal_attempt:
                if steal_ball():
                    messages.append("You stole the ball!")
                else:
                    messages.append("Steal failed.")
            else:
                messages.append("You let them pass.")
        else:
            if score2points():
                opponent_score += 2
                messages.append("Your opponent scored 2 points!")
            else:
                messages.append("Your opponent missed.")

    elif action_type == 'steal':
        messages.append("Steal can only be used as a reaction, not standalone.")

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
