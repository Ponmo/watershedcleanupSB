from flask import Flask, redirect, Markup, url_for, session, request, jsonify
from flask import render_template

import pprint
import os
import sys
from datetime import datetime, timedelta
import gspread

app = Flask(__name__)

connection = os.environ['private_key']
gc = gspread.service_account()

@app.route('/')
def render_layout():
    return render_template('layout.html')
