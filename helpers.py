import requests

from flask import redirect, render_template, session
from functools import wraps

# Adapted from week 9 CS50 finance problem / https://flask.palletsprojects.com/en/latest/patterns/viewdecorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function