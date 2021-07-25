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
    counter = len(data_old) - 1
    while counter >= 0:
        while len(data_old[counter]) > 8:
            data_old[counter].pop(len(data_old[counter]) - 1)
        counter -= 1
    data_intermediate = []
    for row in data_new:
        if row[1] != '' and is_number(row[2]) and row[3] != '' and '/' in row[3] and row[4] != '' and is_number(row[5]) and is_number(row[7]) and is_number(row[8]):
            data_intermediate.append(row)
    data_update = [['a. Name', 'b. People', 'c. Date', 'Color', 'd. Place(s)', 'f. Bag(s)', 'e. Weight (lbs)', 'g. Time (hrs)']]
    data_new = []
    colors = ['#ff0000', '#ff8800', '#ffdd00', '#0dff00', '#00ffc8', '#0080ff', '#0011ff', '#7700ff', '#ff00f2', '#ff0000', '#000000', '#ffffff']
    for row in data_intermediate:
        month = int(row[3].split("/")[0])
        month = colors[month - 1]
        data_update.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8]])
        data_new.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[15]])
    counter = len(data_old) - len(data_update)
    while counter > 0:
        data_update.append(['', '', '', '', '', '', '', ''])
        counter -= 1
    if data_update != data_old:
        wsheet.update('A1:H' + str(len(data_update)), data_update)
    else:
        return render_template('map.html', data = 'worked', data2 = 'worked', data3 = 'worked')
    return render_template('map.html', data = data_old, data2 = data_update, data3 = data_new)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

