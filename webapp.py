#handle exceptions to gspread calls
#change geosheet calls
#sanitize inputs
#while loop that goes through 12 times. Three long strings generated with list of months[cpuntweer] calculate each statistic at the cac

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
gsheet_raw = gp.open('Watershed Brigade')
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
        if row[1] != '' and is_number(row[2]) and '/' in row[3] and row[4] != '' and row[16] != '': #and is_number(row[5]) and is_number(row[7]) and is_number(row[8]) and row[16] != '':
            data_map.append(row)
        if row[1] != '' and is_number(row[2]) and '/' in row[3] and row[4] != '':
            data_stat.append(row)
    data_update = [['a. Name', 'b. People', 'c. Date', 'Color', 'd. Place(s)', 'f. Bag(s)', 'e. Weight (lbs)', 'g. Time (hrs)', 'Location', 'Month']] 
    data_new = []
    colors = ['#edff00', '#f4ef00', '#f9de00', '#fecd00', '#ffbb00', '#ffa900', '#ff9700', '#ff8300', '#ff6e00', '#ff5700', '#ff3a00', '#ff0000']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data_stat:
        month = int(row[3].split("/")[0])
        data_new.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[9], row[15], row[16]])
    counter = 0
    index = 0
    increment = int(len(data_map)/12)
    for row in data_map:
        month = int(row[3].split("/")[0])
        color = colors[index]
        if counter == increment and index < 11:
            counter = 0
            index += 1
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
            if is_number(row[8]):
                if row[0] in participants:
                    participants[row[0]] += float(row[9])
                else:
                    participants[row[0]] = float(row[9])
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
    rankings_bottom = ''
    while place <= len(participants):
        rankings_bottom += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + '. ' + participants[place - 1][0] + 
                            '</p></div><div class="points"><p><b>' + str(participants[place - 1][1]) + '</b></p></div></div></td></tr>')
        place += 1
    return render_template('ranks.html', first = first, second = second, third = third, first_score = first_score, second_score = second_score, third_score = third_score, rankings_bottom = Markup(rankings_bottom))

@app.route('/stats')
def render_stats():
    data = get_data()
    total_trash = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_volunteers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_sites = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_cleanups = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_persons = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    coords = []
    names = []
    month = 1
    chart_data = {}
    end_point = 0.0
    colors = ['#ffb600', '#ff9900', '#ff7900', '#ff5200', '#ff0000']
    index = 0
    for row in data:
        total_cleanups[row[3] - 1] += 1
        if is_number(row[6]):
            total_trash[row[3] - 1] += float(row[6])
        if is_number(row[7]):
            total_time[row[3] - 1] += float(row[7])
        if row[0] not in names:
            total_volunteers[row[3] - 1] += 1
            names.append(row[0])
        if month != row[3]:
            month = row[3]
            coords = []
            names = []
        if is_number(row[1]):
            total_persons[row[3] - 1] += float(row[1])
            if float(row[1]) <= 1:
                index = 0
            elif float(row[1]) <= 5:
                index = 1
            elif float(row[1]) <= 10:
                index = 2
            elif float(row[1]) <= 20:
                index = 3
            else:
                index = 4
            if is_number(row[6]) and is_number(row[8]):
                if str(row[1]) in chart_data:
                    chart_data[str(row[1])] = chart_data.get(str(row[1])) +'{ x: ' + str(row[8]) + ', y: ' + str(row[6]) + ', color: "' + colors[index] + '" },'
                else:
                    chart_data[str(row[1])] = '{ x: ' + str(row[8]) + ', y: ' + str(row[6]) + ', color: "' + colors[index] + '" },'
                if float(row[8]) > end_point:
                    end_point = float(row[8])
        try:
            x_coord = float(row[10].partition(',')[0])
            y_coord = float(row[10].partition(',')[2])
            similar = False
            if coords != []:
                for item in coords:
                    item_x = float(item.partition(',')[0])
                    item_y = float(item.partition(',')[2])
                    if item_x > x_coord - 0.00002 and item_x < x_coord + 0.00002 and item_y > y_coord - 0.00002 and item_y < y_coord + 0.00002:
                        similar = True
            else:
                coords.append(row[10])
            if similar == False:
                total_sites[row[3] - 1] += 1
            else:
                coords.append(row[10])
        except:
            pass
    counter = 1
    chart = ''
    trend_line = ''
    for key in chart_data:
        chart_data[key] = chart_data.get(key)[:-1]
        chart += ('{' +
                  'type: "scatter",' +
                  'name: "' + key + ' Person Group",' +
                  'indexLabelFontSize: 16,' +
                  'toolTipContent: "<span style=\\"color:#4F81BC \\"><b>{name}</b></span><br/><b> Time: </b> {x} hrs<br/><b> Weight of Trash </b></span> {y} lbs",' +
                  'dataPoints: [')
        chart += chart_data.get(key)
        chart += ']}'
        if counter < len(chart_data):
            chart += ','
            trend_line += 'chart.data[' + str(counter) + '].dataPoints,'
        counter += 1
    trend_line = trend_line[:-1]
    counter = 0
    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
    table = ''
    histogram_weight = ''
    histogram_persons = ''
    histogram_time = ''
    while counter < 12:
        if total_trash[counter] != 0.0 and total_volunteers[counter] != 0 and total_sites[counter] != 0:
            table += '<tr><td class="cell no-bold">' + months[counter] + '</td><td class="cell">' + str(total_sites[counter]) + '</td><td class="cell">' + str(total_volunteers[counter]) + '</td><td class="cell">' + str(round(total_trash[counter], 2)) + '</td></tr>' 
        else:
            table += '<tr><td class="cell no-bold">' + months[counter] + '</td><td class="cell"></td><td class="cell"></td><td class="cell"></td></tr>' 
        if total_trash[counter] != 0.0 and total_cleanups[counter] != 0 and total_persons[counter] != 0.0 and total_time[counter] != 0.0:
            histogram_weight += '{ label: "' + months[counter] + '", y: ' + str(total_trash[counter]//total_cleanups[counter]) + ' },'
            histogram_persons += '{ label: "' + months[counter] + '", y: ' + str(total_persons[counter]//total_cleanups[counter]) + ' },'
            histogram_time += '{ label: "' + months[counter] + '", y: ' + str(total_time[counter]//total_cleanups[counter]) + ' },'
        counter += 1
    histogram_weight = histogram_weight[:-1]
    histogram_persons = histogram_persons[:-1]
    histogram_time = histogram_time[:-1]
    return render_template('stats.html', year = datetime.now().strftime('%Y'), table = Markup(table), chart = Markup(chart), trend_line = Markup(trend_line), end_point = Markup(end_point), histogram_weight = Markup(histogram_weight), histogram_persons = Markup(histogram_persons), histogram_time = Markup(histogram_time), test = histogram_persons + histogram_weight + histogram_time)

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
    return render_maps()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
            
