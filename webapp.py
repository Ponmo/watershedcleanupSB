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

@app.route('/') #change start route later?
def render_map():
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
    wsheet = gsheet.get_worksheet(1)
    data_old = wsheet.get_all_values()
    data_intermediate = []
    for row in data_new:
        if row[1] != '' and is_number(row[2]) and row[3] != '' and '/' in row[3] and row[4] != '' and is_number(row[5]) and is_number(row[7]) and is_number(row[8]):
            data_intermediate.append(row)
    data_update = [['Name', '# of People', 'Date', 'Month', 'Location', 'Bags of Trash', 'Weight (lbs)', 'Time (hrs)', 'Points']]
    for row in data_intermediate:
        month = row[3].split("/")[0]
        month = int(month)
        data_update.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[15]])
    counter = len(data_old) - len(data_update)
    for counter > 0:
        data_update.append(['', '', '', '', '', '', '', '', ''])
    if data_update != data_old:
        #wsheet.update('A1:I' + str(len(data_old)), '')
        #gsheet.del_worksheet(wsheet)
        #gsheet.add_worksheet(title='This Year', rows='10000', cols='20')
        wsheet.update('A1:I' + str(len(data_update)), data_update)
    return render_template('map.html', data = data_update)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
