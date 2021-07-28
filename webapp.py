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
    try:
        wsheet = gsheet.worksheet(utc_year + ' WB Tracking')
    except:
        wsheet = gsheet.worksheet(str(int(utc_year) - 1) + ' WB Tracking')
    data_new = wsheet.get_all_values()
    gsheet = gp.open('Watershed Brigade Information')
    wsheet = gsheet.worksheet('This Year')
    data_old = wsheet.get_all_values()
    counter = len(data_old) - 1
    while counter >= 0:
        while len(data_old[counter]) > 10:
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
    counter = 0
    counter_two = int(len(data_map)/12)
    for row in data_map:
        month = int(row[3].split("/")[0])
        color = ''
        if counter < counter_two:
            color = colors[0] 
        elif counter < 2 * counter_two:
            color = colors[1] 
        elif counter < 3 * counter_two:
            color = colors[2] 
        elif counter < 4 * counter_two:
            color = colors[3] 
        elif counter < 5 * counter_two:
            color = colors[4] 
        elif counter < 6 * counter_two:
            color = colors[5] 
        elif counter < 7 * counter_two:
            color = colors[6] 
        elif counter < 8 * counter_two:
            color = colors[7] 
        elif counter < 9 * counter_two:
            color = colors[8] 
        elif counter < 10 * counter_two:
            color = colors[9] 
        elif counter < 11 * counter_two:
            color = colors[10] 
        else:
            color = colors[11] 
        month = months[month - 1]
        data_update.append([row[1], row[2], row[3], color, row[4], row[5], row[7], row[8], row[16], month])
        counter += 1
    counter = len(data_old) - len(data_update)
    while counter > 0: #adds any necessary blank rows to replace old rows in case the number of new rows is less than the number of old rows 
        data_update.append(['', '', '', '', '', '', '', '', '', ''])
        counter -= 1
    if data_update != data_old:
        wsheet.update('A1:J' + str(len(data_update)), data_update)
        wsheet.update_cells(cells, 'USER_ENTERED')
        wsheet.update('K1', '=GEO_MAP(A1:J' + str(len(data_update)) + ', "cleanups", "Location")')
    return data_new

@app.route('/') #change start route later?
def render_map():
    data = get_data()
    checkboxes = ""
    month = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data:
        if row[3] not in month:
            month.append(row[3])
    for item in month:
        checkboxes += "<label class='checkbox-inline'><input type='checkbox' value='" + months[item - 1] + "' class='Month' id='" + months[item - 1] + "' checked>" + months[item - 1] + "</label>"
    return render_template('main.html', checkboxes = Markup(checkboxes))

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

