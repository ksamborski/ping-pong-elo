from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append(os.getcwd())
from elopy import *

app = Flask(__name__)
rating = Implementation()


def load_data_from_file(rating):
    token = None
    try:
        token_file = open('token.txt', 'r')
        token = token_file.read().strip()
        token_file.close()
        rating_file = open('ratings.txt', 'r')
        for player_data in rating_file.readlines():
            player_data_array = player_data.split('_')
            rating.addPlayer(player_data_array[0], float(player_data_array[1]), int(player_data_array[2]),
                        int(player_data_array[3]), float(player_data_array[4]), int(player_data_array[5]))
        rating_file.close()
        match_file = open('matches.txt', 'r')
        for match_data in match_file.readlines():
            if '_' in match_data:
                match_data_array = match_data.split('_')
                rating.addMatchToList(match_data_array[0], match_data_array[1].rstrip())
        match_file.close()
    except FileNotFoundError:
        if token is None:
            raise Exception('Token cannot be empty!')

    return token


token = load_data_from_file(rating)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin',  methods=('GET', 'POST'))
def admin():
    if request.method == 'POST':
        if len(request.form) == 1:
            if request.form['playername'].split(' ', 1)[0] == token:
                rating.addPlayer(request.form['playername'].split(' ', 1)[1])
        else:
            if request.form['victorious'].split(' ', 1)[0] == token:
                victorious = request.form['victorious'].split(' ', 1)[1]
                record_match_and_update_files(rating, victorious, request.form['defeated'])

    return render_template('admin.html', rating_list=rating.getRatingList(), matches_list = rating.getMatchesList())


@app.route('/ping-pong')
def ping_pong():
    return render_template('ping-pong.html', rating_list=rating.getRatingList(), matches_list = rating.getMatchesList())


@app.route('/get_ratings')
def get_ratings():
    array = []
    for player_rating in rating.getRatingList():
        dict = {}
        dict['name'] = player_rating[0]
        dict['rating'] = player_rating[1]
        dict['matches'] = player_rating[2]
        dict['win_streak'] = player_rating[3]
        dict['highest_rating'] = player_rating[4]
        dict['rank_image'] = player_rating[5]
        dict['victories'] = player_rating[6]
        array.append(dict)

    return jsonify(array)


@app.route('/fifa')
def fifa():
    return render_template('fifa.html')


def record_match_and_update_files(rating, victorius, defeated, rating_file='ratings.txt', match_file='matches.txt'):
    rating.recordMatch(victorius, defeated, winner=victorius)
    save_ratings_to_file(rating, rating_file)
    save_matches_to_file(rating, match_file)


def save_ratings_to_file(rating, file_name="ratings.txt"):
    rating_file = open(file_name, "w+")
    for (player, ranking, matches, win_streak, highest_rating, rank_image, victories) in rating.getRatingList():
        rating_file.write("{}_{}_{}_{}_{}_{}\n".format(player, ranking, matches, win_streak, highest_rating, victories))
    rating_file.close()


def save_matches_to_file(rating, file_name="matches.txt"):
    match_file = open(file_name, "w+")
    for (winner, defeated) in rating.getMatchesList():
        match_file.write("{}_{}\n".format(winner, defeated))
    match_file.close()