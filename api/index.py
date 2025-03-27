from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path so app.py can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import app as flask_app

# This is the handler that Vercel will call
def handler(request, context):
    return flask_app 