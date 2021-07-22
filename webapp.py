from flask import Flask, redirect, Markup, url_for, session, request, jsonify
from flask import render_template

import pprint
import os
import sys
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

credentials = {
    'type': 'service_account',
    'project_id': os.environ['project_id'],
    'private_key_id': os.environ['private_key_id'],
    'private_key': os.environ['private_key'].replace('\\n', '\n'),
    'client_email': os.environ['client_email'],
    'client_id': os.environ['client_id'],
    'auth_uri': os.environ['auth_uri'],
    'token_uri': os.environ['token_uri'],
    'auth_provider_x509_cert_url': os.environ['auth_provider_x509_cert_url'],
    'client_x509_cert_url': os.environ['client_x509_cert_url']
}
utc_year = datetime.now().strftime('%Y')
gp = gspread.service_account_from_dict(credentials)
gsheet = gp.open('Copy of Watershed Brigade')
wsheet = gsheet.worksheet(utc_year + ' WB Tracking')
data_new = wsheet.get_all_values()
gsheet = gp.open('Watershed Brigade Information')
wsheet = gsheet.worksheet('Sheet1')
data_old = wsheet.get_all_values()
data_intermediate = []
for row in data_new:
    if row[1] != '' and row[2].isnumeric() and row[3] != '' and row[4] != '' and row[5].isnumeric() and row[7].isnumeric() and row[8].isnumeric() and row[15].isnumeric():
        data_intermediate.append(row)
if data_intermediate != data_old:
    gsheet.del_worksheet(wsheet)
    gsheet.add_worksheet(title="Sheet1", rows="100", cols="20")

@app.route('/') #change start route later?
def render_map():
    return render_template('map.html', data = wsheet.get_all_values())
