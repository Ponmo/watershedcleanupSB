from flask import Flask, redirect, Markup, url_for, session, request, jsonify
from flask import render_template

import pprint
import os
import sys
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def render_layout():
    return render_template('layout.html')
