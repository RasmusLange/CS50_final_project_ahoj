from flask import Flask, flash, redirect, render_template, request, session

from cs50 import SQL

from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ahoj.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    username = db.execute(
        f"SELECT username FROM users WHERE id = {session.get("user_id")}"
    )[0].get("username")

    visit_times = db.execute("""
        SELECT m.message, m.board_id, board_name, u.username
        FROM members AS m
        JOIN members AS current_user
        ON m.board_id = current_user.board_id
        JOIN boards
        ON m.board_id = boards.id
        JOIN users AS u
        ON m.user_id = u.id
        WHERE current_user.user_id = ? AND m.user_id != current_user.user_id AND m.post_time IS NOT NULL AND m.post_time >= current_user.visit_time;""", session.get("user_id"))

    return render_template("index.html", board_messages=visit_times, user=username)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username = db.execute(
        "SELECT username FROM users WHERE id = ?", session.get("user_id")
    )[0].get("username")
    if request.method == "POST":
        change_password = request.form.get("change_password")
        change_username = request.form.get("change_username")
        new_password = request.form.get("new_password")
        new_username = request.form.get("new_username")
        if not change_password and not change_username:
            return render_template("account.html", username=username, message="No changes made", message_type="neutral")
        if change_password and change_username:
            if not new_password or not new_username:
                return render_template("account.html", username=username, message="Please specify both new username and password")
            else:
                return render_template("account.html", username=username, message=f"Username changed to {new_username} and password updated!", message_type="good")
        if not change_password and change_username:
            if not new_username:
                return render_template("account.html", username=username, message="Please specify new username")
            else:
                return render_template("account.html", username=username, message=f"Username changed to {new_username}!", message_type="good")
        if change_password and not change_username:
            if not new_password:
                return render_template("account.html", username=username, message="Please specify new password")
            else:
                return render_template("account.html", username=username, message=f"Password updated!", message_type="good")
    else:
        return render_template("account.html", username=username)

@app.route("/board", methods=["GET", "POST"])
@login_required
def board():
    if request.method == "POST":
        board_id = request.form.get("visit")
        post_message = request.form.get("post-message")
        promote = request.form.get("promote")
        kick = request.form.get("kick")
        if not board_id:
            return render_template("index.html", message="Board not found")
        db.execute(
            "UPDATE members SET visit_time = unixepoch() WHERE user_id = ? AND board_id = ?", session.get("user_id"), board_id
        )
        board_name = db.execute(
            "SELECT board_name FROM boards WHERE id = ?", session.get("user_id")
        )[0].get("board_name")
        board_messages = db.execute(
            "SELECT message, username, board_id, admin, user_id FROM members JOIN users ON members.user_id = users.id WHERE board_id = ? ", board_id
        )
        current_user = db.execute(
            "SELECT username, admin FROM users JOIN members ON users.id = members.user_id WHERE users.id = ?", session.get("user_id")
        )[0]
        if kick and session.get("user_id") != kick:
            db.execute(
                "DELETE FROM members WHERE user_id = ? AND board_id = ?", kick, board_id
            )
            board_messages = db.execute(
                "SELECT message, username, board_id, admin, user_id FROM members JOIN users ON members.user_id = users.id WHERE board_id = ? ", board_id
            )
            return render_template("board.html", board_name=board_name, board_messages=board_messages, board_id=board_id, current_user=current_user)
        if promote and session.get("user_id") != promote:
            user_admin = db.execute(
                "SELECT admin FROM members WHERE user_id = ? AND board_id = ?", promote, board_id
            )[0].get("admin")
            if user_admin == 1:
                db.execute(
                    "UPDATE members SET admin = 0 WHERE user_id = ? AND board_id = ?", promote, board_id
                )
            else:
                db.execute(
                    "UPDATE members SET admin = 1 WHERE user_id = ? AND board_id = ?", promote, board_id
                )
            board_messages = db.execute(
                "SELECT message, username, board_id, admin, user_id FROM members JOIN users ON members.user_id = users.id WHERE board_id = ? ", board_id
            )
            return render_template("board.html", board_name=board_name, board_messages=board_messages, board_id=board_id, current_user=current_user)
        if not post_message:
            return render_template("board.html", board_name=board_name, board_messages=board_messages, board_id=board_id, current_user=current_user)
        else:
            db.execute(
                "UPDATE members SET message = ?, post_time = unixepoch() WHERE board_id = ? AND user_id = ?", post_message, board_id, session.get("user_id")
            )
            board_messages = db.execute(
                "SELECT message, username, board_id, admin FROM members JOIN users ON members.user_id = users.id WHERE board_id = ? ", board_id
            )
            return render_template("board.html", board_name=board_name, board_messages=board_messages, board_id=board_id, current_user=current_user)
    else:
        return render_template("index.html", message="Board not found")

@app.route("/boards", methods=["GET", "POST"])
@login_required
def boards():
    if request.method == "POST":
        leave_board = request.form.get("leave")
        db.execute(
            "DELETE FROM members WHERE user_id = ? AND board_id = ?", session.get("user_id"), leave_board
        )
        data = db.execute(
            "SELECT board_id FROM members WHERE user_id = ?", session.get("user_id")
        )
        values = [str(item['board_id']) for item in data]
        placeholders = ",".join("?" for _ in values)
        query = f"SELECT board_name, id FROM boards WHERE id IN ({placeholders})"
        board_names = db.execute(query, *values)
        return render_template("boards.html", boards=board_names, message="Successfully left board")
    else:
        data = db.execute(
            "SELECT board_id FROM members WHERE user_id = ?", session.get("user_id")
        )
        values = [str(item['board_id']) for item in data]
        placeholders = ",".join("?" for _ in values)
        query = f"SELECT board_name, id FROM boards WHERE id IN ({placeholders})"
        board_names = db.execute(query, *values)
        return render_template("boards.html", boards=board_names)

@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        board = request.form.get("board")
        if not board:
            return render_template("join.html", message="Please provide a board name")
        board_search = db.execute(
            "SELECT id FROM boards WHERE board_name = ?", board
        )
        if len(board_search) == 0:
            db.execute(
                "INSERT INTO boards (board_name) VALUES (?)", board
            )
            new_search = db.execute(
                "SELECT id FROM boards WHERE board_name = ?", board
            )[0].get("id")
            db.execute(
                "INSERT INTO members (user_id, board_id, admin, message) VALUES (?, ?, ?, '!RLDEL!')", session.get("user_id"), new_search, 1
            )
            return render_template("join.html", message="Board created")
        else:
            new_search = db.execute(
                "SELECT id FROM boards WHERE board_name = ?", board
            )[0].get("id")
            relation_search = db.execute(
                "SELECT * FROM members WHERE user_id = ? AND board_id = ?", session.get("user_id"), new_search
            )
            if len(relation_search) == 0:
                db.execute(
                    "INSERT INTO members (user_id, board_id, admin, message) VALUES (?, ?, ?, '!RLDEL!')", session.get("user_id"), new_search, 0
                )
                return render_template("join.html", message="Board joined!")
            else:
                return render_template("join.html", message="You're already a member of this board")
    return render_template("join.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Adapted from CS50 Finanace problem
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", message="Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="Must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", message="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return render_template("register.html", message="Please provide username")
        if not password:
            return render_template("register.html", message="Please provide password")
        if not confirmation:
            return render_template("register.html", message="Please provide password confirmation")
        if password != confirmation:
            return render_template("register.html", message="Passwords don't match")
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password, method='scrypt', salt_length=16)
        )
        return render_template("register.html", message="User succesfully registered", message_type="good")
    else:
        return render_template("register.html")

