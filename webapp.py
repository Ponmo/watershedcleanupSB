from flask import Flask, redirect, Markup, url_for, session, request, jsonify
from flask import render_template

import pprint
import os
import sys
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

app = Flask(__name__)

gp = gspread.service_account(filename='watershedlittersb-eb911cf106c1.json')

@app.route('/')
def render_layout():
    return render_template('layout.html')
