#handle exceptions to gspread calls
#handle colors
#change geosheet calls

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

def get_data():
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
    wsheet = gsheet.worksheet('This Year')
    data_old = wsheet.get_all_values()
    counter = len(data_old) - 1
    while counter >= 0:
        while len(data_old[counter]) > 9:
            data_old[counter].pop(len(data_old[counter]) - 1)
        counter -= 1
    data_map = []
    data_stat = []
    for row in data_new:
        if row[1] != '' and is_number(row[2]) and row[3] != '' and '/' in row[3] and row[4] != '' and row[16] != '': #and is_number(row[5]) and is_number(row[7]) and is_number(row[8]) and row[16] != '':
            data_map.append(row)
        if row[1] != '' and is_number(row[2]) and row[3] != '' and '/' in row[3] and row[4] != '':
            data_stat.append(row)
    data_update = [['a. Name', 'b. People', 'c. Date', 'Color', 'd. Place(s)', 'f. Bag(s)', 'e. Weight (lbs)', 'g. Time (hrs)', 'Location', 'Month']] 
    data_new = []
    colors = ['#000000', '#171717', '#2e2e2e', '#464646', '#5d5d5d', '#747474', '#8b8b8b', '#a2a2a2', '#b9b9b9', '#d1d1d1', '#e8e8e8', '#ffffff']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data_stat:
        month = int(row[3].split("/")[0])
        data_new.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[15]])
    for row in data_map:
        month = int(row[3].split("/")[0])
        color = colors[month - 1]
        month = months[month - 1]
        data_update.append([row[1], row[2], row[3], color, row[4], row[5], row[7], row[8], row[16], month])
    counter = len(data_old) - len(data_update)
    while counter > 0: #adds any necessary blank rows to replace old rows in case the number of new rows is less than the number of old rows 
        data_update.append(['', '', '', '', '', '', '', '', '', ''])
        counter -= 1
    if data_update != data_old:
        wsheet.update('A1:J' + str(len(data_update)), data_update)
    return len(data_new)

@app.route('/') #change start route later?
def render_map():
    data = get_data()
    return render_template('map.html', data = data)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

