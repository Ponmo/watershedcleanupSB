#handle exceptions to gspread calls
#change geosheet calls
#sanitize inputs

from flask import Flask, redirect, Markup, url_for, session, request, jsonify
from flask import render_template

import pprint
import os
import sys
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, date, timedelta
from pytz import timezone
import pytz

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
gp = gspread.service_account_from_dict(credentials)
gsheet_raw = gp.open('Copy of Watershed Brigade')
gsheet = gp.open('Watershed Brigade Information')

def get_data():
    utc_year = datetime.now().strftime('%Y')
    try:
        wsheet = gsheet_raw.worksheet(utc_year + ' WB Tracking')
    except:
        wsheet = gsheet_raw.worksheet(str(int(utc_year) - 1) + ' WB Tracking')
    data_new = wsheet.get_all_values()
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
    colors = ['#edff00', '#f4ef00', '#f9de00', '#fecd00', '#ffbb00', '#ffa900', '#ff9700', '#ff8300', '#ff6e00', '#ff5700', '#ff3a00', '#ff0000']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data_stat:
        month = int(row[3].split("/")[0])
        data_new.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[15], row[16]])
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
        elif counter < 11 * counter_two: #first get variable equal to increment. Counter equal to how many. First color var equal to color[0] if counter = increment then color equal to color[+1]
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
        cell = wsheet.range('K1:K1')
        cell[0].value = '=GEO_MAP(A1:J' + str(len(data_update)) + ', "cleanups", "Location")'
        wsheet.update_cells(cell, 'USER_ENTERED')
    wsheet = gsheet.worksheet('Reports')
    data_report = wsheet.get_all_values()
    date_now = datetime.now(tz=pytz.utc)
    date_now = date_now.astimezone(timezone('America/Los_Angeles'))
    counter = 0
    counter_two = 0
    counter_three = 0
    change = False
    for row in data_report:
        if '/' in row[4]:
            if row[3] != 'Not resolved' and row[5] != '#4285F4':
                data_report[counter_three][5] = '#4285F4'
                change = True
            date_report = row[4].partition('/')
            date_report = datetime(int(date_report[2].partition("/")[2]), int(date_report[0]), int(date_report[2].partition("/")[0]), 0, 0, 0, 0, tzinfo=pytz.utc)
            delta = date_now - date_report
            if delta.days > 30:
                data_report.remove(row)
                counter_two += 1
                change = True
        counter_three += 1
    while counter_two > 0:
        data_report.append(['', '', '', '', '', ''])
        counter_two -= 1
    if change == True:
        wsheet.update('A1:G' + str(len(data_report)), data_report)
        cell = wsheet.range('G1:G1')
        cell[0].value = '=GEO_MAP(A1:F' + str(len(data_report)) + ', "reports", "Location")'
        wsheet.update_cells(cell, 'USER_ENTERED')
    return data_new

@app.route('/') #change start route later?
def render_maps():
    data = get_data()
    checkboxes = ''
    month = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data:
        if row[3] not in month:
            month.append(row[3])
    for item in month:
        checkboxes += '<label class="checkbox-inline"><input type="checkbox" value="' + months[item - 1] + '" class="Month" id="' + months[item - 1] + '" checked>' + months[item - 1] + '</label>'
    wsheet = gsheet.worksheet('Reports')
    data_report = wsheet.get_all_values()
    reports = 0
    disable = ''
    report_limit = ''
    date_now = datetime.now(tz=pytz.utc)
    date_now = date_now.astimezone(timezone('America/Los_Angeles'))
    for row in data_report:
        if row[4] == date_now.strftime('%m/%d/%Y'):
            reports += 1
        if reports >= 10:
            report_limit = '<p id="report-limit">The maximum number of reports have been reached, please try tomorrow.</p>'
            disable = 'disabled'
    return render_template('maps.html', checkboxes = Markup(checkboxes), report_limit = Markup(report_limit), submit = disable)

@app.route('/ranks')
def render_ranks():
    data = get_data()
    month = int(data[len(data) - 1][2].partition('/')[0])
    participants = {}
    for row in data:
        if int(row[2].partition('/')[0]) == month:
            if is_number(row[7]):
                if row[0] in participants:
                    participants[row[0]] += float(row[7])
                else:
                    participants[row[0]] = float(row[7])
    participants = sorted(participants.items(), key=lambda x: x[1], reverse=True)
    first = ''
    second = ''
    third = ''
    first_score = ''
    second_score = ''
    third_score = ''
    if len(participants) >= 1:
        first = participants[0][0]
        first_score = str(participants[0][1])
    if len(participants) >= 2:
        second = participants[1][0]
        second_score = str(participants[1][1])
    if len(participants) >= 3:
        third = participants[2][0]
        third_score = str(participants[2][1])
    place = 4
    counter = 0
    rankings_bottom = ''
    while counter < 7:
        if place < len(participants):
            rankings_bottom += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + '. ' + participants[place - 1][0] + 
                                '</p></div><div class="points"><p><b>' + str(participants[place - 1][1]) + '</b></p></div></div></td></tr>')
        else:
            rankings_bottom += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + 
                                '.</p></div><div class="points"><p></p></div></div></td></tr>')
        counter += 1
        place += 1
    return render_template('ranks.html', first = first, second = second, third = third, first_score = first_score, second_score = second_score, third_score = third_score, rankings_bottom = Markup(rankings_bottom))

@app.route('/stats')
def render_stats():
    data = get_data()
    total_trash = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_volunteers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_sites = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    coords = []
    names = []
    for row in data:
        if is_number(row[6]):
            total_trash[row[3] - 1] += float(row[6])
        if row[0] not in names:
            total_volunteers[row[3] - 1] += 1
            names.append(row[0])
        try:
            x_coord = float(row[9].partition(',')[0])
            y_coord = float(row[9].partition(',')[2])
            similar = False
            if coords != []:
                for item in coords:
                    item_x = float(item.partition(',')[0])
                    item_y = float(item.partition(',')[2])
                    if item_x > x_coord - 0.00002 and item_x < x_coord + 0.00002 and item_y > y_coord - 0.00002 and item_y < y_coord + 0.00002:
                        similar = True
                        #total_sites[row[3] - 1] += 1
            else:
                coords.append(row[9])
            if similar == True:
                total_sites[row[3] - 1] += 1
            else:
                coords.append(row[9])
        except:
    return render_template('stats.html', test = total_sites)

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        gsheet = gp.open('Watershed Brigade Information')
        wsheet = gsheet.worksheet('Reports')
        data_report = wsheet.get_all_values()
        counter = 0
        counter_two = 0
        counter_three = 0
        date_now = datetime.now(tz=pytz.utc)
        date_now = date_now.astimezone(timezone('America/Los_Angeles'))
        data_report.append([request.form['coords'], request.form['trash'], request.form['comment'], 'Not resolved', date_now.strftime('%m/%d/%Y'), '#DB4437'])
        wsheet.update('A1:G' + str(len(data_report)), data_report)
        cell = wsheet.range('G1:G1')
        cell[0].value = '=GEO_MAP(A1:F' + str(len(data_report)) + ', "reports", "Location")'
        wsheet.update_cells(cell, 'USER_ENTERED')
    return render_map()
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
            
