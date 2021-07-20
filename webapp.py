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

#put on render page with map
gp = gspread.service_account(filename='watershedlittersb-eb911cf106c1.json')
gsheet = gp.open('Watershed Brigade Clean-up and Point Request Form (Responses)')
wsheet = gsheet.worksheet("Sheet1")

@app.route('/')
def render_layout():
    return render_template('layout.html', data = wsheet.get_all_values())
