import time
from flask import current_app as app, request
import json

from app.functions.game import get_curr_location, next_play, prepare_new_round
from app.functions.guess import collect_cards, get_guesses, give_guess
from app.functions.play import get_curr_cards, get_curr_wins, get_current_play, give_play
from app.functions.result import get_curr_results
from app.functions.start import change_num_cards, create_new_game, join_game, start_game, update_start_screen
from app.functions.token import token_check
from app.models import Game, Play, User, db

from app.functions.start import words_for_id

@app.before_first_request
def load_words():
    
    global words_for_id
    
    with open("nouns.txt") as f:
        words = f.readlines()
    
    for word in words:
        word = word.capitalize()
        words_for_id.append(word[:-1])

@app.before_request
def check_db():
    # TODO Find a better solution to this. Current solution implemeneted to stop overlap where two requests attempt to do the same action
    try:
        token = request.args.get('token')

        auth_user_id = token_check(token)
        user = User.query.get(auth_user_id)
        
        # Checking for plays to start
        plays = Play.query.filter(Play.round_status == "w", Play.wait_end <= time.time(), Play.current_user_id == auth_user_id).all()

        for play in plays:
            play.round_status = "f"
            next_play(play.game_id, play.round_id) 

        #check for new rounds
        if user.is_owner:
            games = Game.query.filter(Game.game_stage == "R", Game.new_round_time <= time.time(), Game.id == user.game_id).all()

            for game in games:
                prepare_new_round(game.id)
                
        db.session.commit()
    except Exception as e:
        print(e)
        

# Start routes
@app.route("/start/create_game", methods = ["POST"])
def start_create_game():
    data = request.get_json()

    return json.dumps(create_new_game(data['name']))

@app.route("/start/join_game", methods = ["POST"])
def start_join_game():
    data = request.get_json()

    return json.dumps(join_game(data['name'], data['game_id']))

@app.route("/start/change_num_cards", methods = ["POST"])
def start_change_num_cards():
    data = request.get_json()

    auth_user_id = token_check(data['token'])

    change_num_cards(auth_user_id, data['num_cards'])

    return {}

@app.route("/start/update_start_screen", methods = ["GET"])
def start_update_start_screen():

    token = request.args.get('token')

    auth_user_id = token_check(token)

    return json.dumps(update_start_screen(auth_user_id))

@app.route("/start/start_game", methods = ["POST"])
def start_start_game():
    data = request.get_json()

    auth_user_id = token_check(data['token'])

    return json.dumps(start_game(auth_user_id))

# Guess routes
@app.route("/guess/collect_cards", methods = ['GET'])
def guess_collect_cards():
    token = request.args.get('token')
    
    auth_user_id = token_check(token)

    return json.dumps(collect_cards(auth_user_id))

@app.route("/guess/get_guesses", methods = ['GET'])
def guess_get_guesses():
    token = request.args.get('token')

    auth_user_id = token_check(token)

    return json.dumps(get_guesses(auth_user_id))

@app.route("/guess/give_guess", methods = ["POST"])
def guess_give_guess():
    data = request.get_json()

    auth_user_id = token_check(data['token'])

    return json.dumps(give_guess(auth_user_id, data['guess']))

# Play routes
@app.route("/play/get_curr_cards", methods = ['GET'])
def play_get_curr_cards():
    token = request.args.get('token')

    auth_user_id = token_check(token)

    return json.dumps(get_curr_cards(auth_user_id))

@app.route("/play/get_current_play", methods = ['GET'])
def play_get_current_play():
    token = request.args.get('token')

    auth_user_id = token_check(token)

    return json.dumps(get_current_play(auth_user_id))

@app.route("/play/get_curr_wins", methods = ['GET'])
def play_get_curr_wins():
    token = request.args.get('token')

    auth_user_id = token_check(token)

    return json.dumps(get_curr_wins(auth_user_id))

@app.route("/play/give_play", methods = ["POST"])
def play_give_play():
    data = request.get_json()

    auth_user_id = token_check(data['token'])

    return json.dumps(give_play(auth_user_id, data['play']))

# Results routs
@app.route("/result/get_curr_results", methods = ['GET'])
def result_get_curr_results():
    token = request.args.get('token')

    auth_user_id = token_check(token)

    return json.dumps(get_curr_results(auth_user_id))

@app.route("/game/get_curr_location", methods = ['GET'])
def game_get_curr_location():
    token = request.args.get('token')
    
    auth_user_id = token_check(token)
    
    return json.dumps(get_curr_location(auth_user_id))