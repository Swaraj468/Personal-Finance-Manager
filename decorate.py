from functools import wraps
from flask import g, request, redirect
from flask import session
# I have taken reference of this code from flask decorators document
""" 
https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Session in decorator:", session)  # Check if session is accessible
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
        