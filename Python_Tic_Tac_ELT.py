from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Replace with your SQL Server connection details
server = 'localhost'  # IP address and port of the Docker container
database = 'GAME'
username = 'sa'
password = 'reallyStrongPwd123'


# Create a connection string
conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = conn_str
db = SQLAlchemy(app)


class GameStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.String(50), nullable=False)
    player2 = db.Column(db.String(50), nullable=False)
    winner = db.Column(db.String(50), nullable=True)
    game_stats = db.Column(db.String(100), nullable=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player1_name = request.form["player1_name"]
        player2_name = request.form["player2_name"]
        return redirect(url_for("start_game", player1_name=player1_name, player2_name=player2_name))
    return render_template("index.html")


@app.route("/start_game", methods=["GET"])
def start_game():
    player1_name = request.args.get("player1_name")
    player2_name = request.args.get("player2_name")
    try:
        game = GameStats(player1=player1_name, player2=player2_name, game_stats=" " * 9)
        db.session.add(game)
        db.session.commit()
        print(f"Game created: {game.id}")
        return redirect(url_for("game", game_id=game.id))
    except Exception as e:
        print(f"Error creating game: {e}")
        return "Error creating game", 500


@app.route("/game/<int:game_id>")
def game(game_id):
    game = GameStats.query.get(game_id)
    if game is None:
        return "Game not found", 404
    board = list(game.game_stats)
    current_player = game.player1+" --> X" if board.count("X") == board.count("O") else game.player2+" --> O"
    player_turn = (board.count("X") + board.count("O")) + 1
    return render_template("game.html", game_id=game_id, board=board, current_player=current_player, player_turn=player_turn)


@app.route("/make_move", methods=["POST"])
def make_move():
    game_id = int(request.form["game_id"])
    move = int(request.form["move"])
    try:
        game = GameStats.query.get(game_id)
        if game is None:
            return "Game not found", 404
        board = list(game.game_stats)
        current_player = "X" if board.count("X") == board.count("O") else "O"
        board[move - 1] = current_player
        game.game_stats = "".join(board)
        db.session.commit()
        print(f"Move made: {game_id}, {move}, {current_player}")
        if check_win(board):
            game.winner = game.player1 if current_player=="X" else game.player2
            db.session.commit()
            return redirect(url_for("game_over", game_id=game_id))
        elif " " not in board:
            game.winner = "Tie"
            db.session.commit()
            return redirect(url_for("game_over", game_id=game_id))
        return redirect(url_for("game", game_id=game_id))
    except Exception as e:
        print(f"Error making move: {e}")
        return "Error making move", 500

@app.route("/game_over/<int:game_id>")
def game_over(game_id):
    game = GameStats.query.get(game_id)
    if game is None:
        return "Game not found", 404
    board = list(game.game_stats)
    print(board)  # Add this line to print the board
    winner = game.winner
    return render_template("game_over.html", board=board, winner=winner, game_id=game_id)


@app.route("/restart_game", methods=["POST"])
def restart_game():
    # game_id = int(request.form["game_id"])
    # game = GameStats.query.get(game_id)
    # if game is None:
    #     return "Game not found", 404
    # db.session.delete(game)
    # db.session.commit()
    return redirect(url_for("index"))


def check_win(board):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]]!= " ":
            return True
    return False


if __name__ == "__main__":
    app.run(debug=True)