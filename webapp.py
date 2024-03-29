from flask import Flask, redirect, url_for, session, request, jsonify
from markupsafe import Markup
from flask import render_template
from bson import ObjectId

import pprint
import os
import sys
import pymongo
import gspread
from datetime import datetime, date, timedelta
from pytz import timezone
import pytz

app = Flask(__name__)

app.secret_key = os.environ['SECRET_KEY']

connection_string = os.environ['MONGO_CONNECTION_STRING']
db_name = os.environ['MONGO_DBNAME']
client = pymongo.MongoClient(connection_string)
db = client[db_name]
collection = db['Cleanups']
collectionTwo = db['Reports']
collectionThree = db['Update']

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
gsheet = gp.open('Watershed Brigade - Master Tracking Sheet') #Name of Channelkeeper's Google Sheet.

def get_data(): #retrieves data from Channelkeeper's Google Sheet. Updates data if anything is new/changed in the other Google Sheet. Removes old reports from reports map. Returns formatted data as a list of lists to be used for this webapp. 
    data_new = []
    updateMongo = True
    if datetime.now().strftime('%d') == collectionThree.find_one().get('date'):
        updateMongo = False
    #if 'returner' in session:
    #    updateMongo = False
    try:
        utc_year = datetime.now().strftime('%Y')
        try:
            wsheet = gsheet.worksheet(utc_year + ' WB Tracking') #opens the sheet containing cleanups of the current year in Channelkeeper's Google Sheet.
        except:
            wsheet = gsheet.worksheet('2021 WB Tracking') #If a sheet for the current year does not exist yet, it opens up the sheet of the past year.
        data_new = wsheet.get_all_values() #retrieves all the raw data from Channelkeeper's Google Sheet as a list of lists.
        wsheet = gsheet.worksheet('This Year') #opens the sheet in the maps Google Sheet containing data for the cleanups map.
        data_old = wsheet.get_all_values() #retrieves all data from 'This Year' in the maps Google Sheet as a list of lists. 
        counter = len(data_old) - 1
        while counter >= 0: #removes extra columns from data_old (the geosheets formula and any notes)
            while len(data_old[counter]) > 10:
                data_old[counter].pop(len(data_old[counter]) - 1)
            counter -= 1
        data_map = []
        data_stat = []
        for row in data_new: #checks every row of raw data from Channelkeeper's Google Sheet and removes any that are not valid cleanups. It does this by checking if the column containing names is not empty, the date column contains a '/', and the column containing locations is not empty.
            if row[1] != '' and is_number(row[2]) and '/' in row[3] and row[4] != '' and row[16] != '': #in order to be a valid cleanup to be put on the cleanups map, it also checks if the coordinates column is not empty. Make sure it is a valid coordinate, or else a geocoding limit might be reached.
                data_map.append(row) #contains valid cleanups that can be put on maps.
            if row[1] != '' and is_number(row[2]) and '/' in row[3] and row[4] != '':
                data_stat.append(row) #contains valid cleanups.
        data_update = [['a. Name', 'b. People', 'c. Date', 'Color', 'd. Place(s)', 'f. Bag(s)', 'e. Weight (lbs)', 'g. Time (hrs)', 'Location', 'Month']] #first row on the cleanups sheet has these labels
        data_new = []
        colors = ['#ab00ff', '#b300e6', '#bb00cc', '#c400b3', '#cc0099', '#d1008d', '#d50080', '#db006e', '#e0005c', '#e80045', '#ef0030', '#ff0000'] #color gradient used to color points on the cleanups map from old to new.
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] #12 months of the year.
        if updateMongo:
            collectionThree.delete_many({})
            collectionThree.insert_one({'date': datetime.now().strftime('%d')})
            collection.delete_many({})
            for row in data_stat: #organizes and removes any useless data from data_stat and puts them in data_new, which is used by this web app.
                month = int(row[3].split("/")[0]) #obtains the month of the cleanup from its date.
                data_new.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[9], row[15], row[16]])
                generate = ObjectId()
                item = {'_id': generate, '0': row[1], '1': row[2], '2': row[3], '3': month, '4': row[4], '5': row[5], '6': row[7], '7': row[8], '8': row[9], '9': row[15], '10': row[16]}
                collection.insert_one(item)
        else:
            for row in data_stat: #organizes and removes any useless data from data_stat and puts them in data_new, which is used by this web app.
                month = int(row[3].split("/")[0]) #obtains the month of the cleanup from its date.
                data_new.append([row[1], row[2], row[3], month, row[4], row[5], row[7], row[8], row[9], row[15], row[16]])
        counter = 0
        index = 0
        increment = int(len(data_map)/12)
        for row in data_map: #organizes and removes any useless data from data_map and puts them in data_update, which will be updated into the cleanups sheet.
            month = int(row[3].split("/")[0]) #obtains the month of the cleanup from its date.
            color = colors[index]
            if counter == increment and index < 11: #an even color gradient is given to each cleanup.
                counter = 0
                index += 1
            month = months[month - 1] #turns the numbered month from the cleanup date into the month as a word.
            data_update.append([row[1], row[2], row[3], color, row[4], row[5], row[7], row[8], row[16], month])
            counter += 1
        counter = len(data_old) - len(data_update)
        while counter > 0: #adds blank rows to data_update in case the number of cleanups on the cleanups sheet is more than in data_update.
            data_update.append(['', '', '', '', '', '', '', '', '', ''])
            counter -= 1
        if data_update != data_old: #if data_update (new data from Channelkeeper) is different from the data on the cleanups sheet, then it updates the cleanups sheet.
            wsheet.update('A1:J' + str(len(data_update)), data_update)
            cell = wsheet.range('K1:K1')
            cell[0].value = '=GEO_MAP(A1:J' + str(len(data_update)) + ', "cleanups", "Location")' #adds geosheets formula to the cleanups sheet to generate the new map.
            wsheet.update_cells(cell, 'USER_ENTERED')
        wsheet = gsheet.worksheet('Reports') #open up the reports sheet on the maps google Sheet.
        data_report = wsheet.get_all_values() 
        date_now = datetime.now(tz=pytz.utc)
        date_now = date_now.astimezone(timezone('America/Los_Angeles'))
        counter = 0
        counter_two = 0
        counter_three = 0
        change = False
        for row in data_report: #removes any reports from the sheet that is older than a month. Changes the color of the report on the map if it is resolved or anything other than the normal "Not resolved".
            if '/' in row[4]: #checks if the row is a valid report by checking if the date column has a "/".
                if row[3] != 'Not resolved' and row[5] != '#4285F4': #if the status of the report is anything other than "Not resolved", then change the color of the dot.
                    data_report[counter_three][5] = '#4285F4'
                    change = True
                date_report = row[4].partition('/')
                date_report = datetime(int(date_report[2].partition("/")[2]), int(date_report[0]), int(date_report[2].partition("/")[0]), 0, 0, 0, 0, tzinfo=pytz.utc)
                delta = date_now - date_report
                if delta.days > 30: #if the report is over 30 days old, then remove it from the reports sheet.
                    data_report.remove(row)
                    counter_two += 1
                    change = True
            counter_three += 1
        if updateMongo:
            collectionTwo.delete_many({})
            for row in data_report:
                generate = ObjectId()
                item = {'_id': generate, '0': row[0], '1': row[1], '2': row[2], '3': row[3], '4': row[4], '5': row[5]}
                collectionTwo.insert_one(item)
        while counter_two > 0:  #adds blank rows to data_report in case the number of reports on the reports sheet is more than in data_reports.
            data_report.append(['', '', '', '', '', ''])
            counter_two -= 1
        if change == True: #if any changes had to be made to data_reports (old data), then update the reports sheet with new information.
            wsheet.update('A1:G' + str(len(data_report)), data_report)
            cell = wsheet.range('G1:G1')
            cell[0].value = '=GEO_MAP(A1:F' + str(len(data_report)) + ', "reports", "Location")' #adds geosheets formula to the reports sheet to generate the new map.
            wsheet.update_cells(cell, 'USER_ENTERED')
    except:
        cursor = collection.find({})
        for item in cursor:
            data_new.append([item.get('0'), item.get('1'), item.get('2'), item.get('3'), item.get('4'), item.get('5'), item.get('6'), item.get('7'), item.get('8'), item.get('9'), item.get('10')])
    return data_new
            
@app.route('/') 
def render_maps(): #renders the maps page.
    data = get_data() #gets cleanup data.
    checkboxes = ''
    month = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data: #creates a list of all months in which cleanups were done in. 
        if row[3] not in month:
            month.append(row[3])
    for item in month: #adds a checkbox for each month in which cleanups were done so that points from each month can be toggled on or off from the cleanups map.
        checkboxes += '<label class="checkbox-inline"><input type="checkbox" value="' + months[item - 1] + '" class="Month" id="' + months[item - 1] + '" checked>' + months[item - 1] + '</label>'
    data_report = []
    cursor = collectionTwo.find({})
    for item in cursor:
        data_report.append([item.get('0'), item.get('1'), item.get('2'), item.get('3'), item.get('4'), item.get('5')])
    reports = 0
    disable = ''
    report_limit = ''
    date_now = datetime.now(tz=pytz.utc)
    date_now = date_now.astimezone(timezone('America/Los_Angeles'))
    resolve_locations = ''
    for row in data_report: #if the number of reports made on the current date exceed ten, then disable the reports form.
        if row[4] == date_now.strftime('%m/%d/%Y'):
            reports += 1
        if '/' in row[4] and row[3] == 'Not resolved': #generates options for the resolve form.
            resolve_locations += '<option>' + row[0] + '</option>'
    if reports >= 10:
        report_limit = '<p id="report-limit">The maximum number of reports have been reached, please try tomorrow.</p>'
        disable = 'disabled'
    if len(data_report) > 40: #if there are more than 40 reports already, change location question so that it only accepts coordinates. This is to prevent geocoding limits.
        location_question = '<label>Coordinates: ( <input name="x-location" class="form-control" placeholder="34.011761" maxlength="10" type="number" step="0.000001" required> , <input name="y-location" class="form-control" placeholder="-119.777489" maxlength="10" type="number" step="0.000001" required> )</label>'
    else:
        location_question = '<label for="location">Specific Address/Coordinates:&nbsp;</label><input type="text" class="form-control" id="location" maxlength="40" name="location" required>'
    returner = ''
    if 'returner' not in session:
        returner = '<script>$(document).ready(function() { $("#myModal").modal("show");});</script>'
        session['returner'] = 'yes'
    return render_template('maps.html', checkboxes = Markup(checkboxes), location_question = Markup(location_question), report_limit = Markup(report_limit), submit = Markup(disable), resolve_locations = Markup(resolve_locations), returner = Markup(returner))

@app.route('/maps-embed')
def render_maps_embed(): #same as render_maps() except this renders a page without the top bar and background image.
    data = get_data()
    checkboxes = ''
    month = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for row in data:
        if row[3] not in month:
            month.append(row[3])
    for item in month:
        checkboxes += '<label class="checkbox-inline"><input type="checkbox" value="' + months[item - 1] + '" class="Month" id="' + months[item - 1] + '" checked>' + months[item - 1] + '</label>'
    data_report = []
    cursor = collectionTwo.find({})
    for item in cursor:
        data_report.append([item.get('0'), item.get('1'), item.get('2'), item.get('3'), item.get('4'), item.get('5')])
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
    if len(data_report) > 40:
        location_question = '<label>Coordinates: ( <input name="x-location" class="form-control" placeholder="34.011761" maxlength="10" type="number" step="0.000001" required> , <input name="y-location" class="form-control" placeholder="-119.777489" maxlength="10" type="number" step="0.000001" required> )</label>'
    else:
        location_question = '<label for="location">Specific Address/Coordinates:&nbsp;</label><input type="text" class="form-control" id="location" maxlength="40" name="location" required>'
    return render_template('maps-embed.html', checkboxes = Markup(checkboxes), location_question = Markup(location_question), report_limit = Markup(report_limit), submit = disable)

@app.route('/ranks')
def render_ranks(): #renders the ranks page.
    data = get_data() #gets cleanup data.
    latest_year = int(datetime.now().strftime('%y'))
    for row in data:
        year = abs(int(row[2].partition('/')[2].partition('/')[2])) % 100
        if year > latest_year:
            latest_year = year
    latest_month = 1
    for row in data:
        if int(row[2].partition('/')[0]) > latest_month and abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == latest_year:
            latest_month = int(row[2].partition('/')[0])
    participants = {}
    participants_year = {}
    for row in data: #checks every cleanup. Checks if the cleanup was conducted in the current month, and if it has points. It counts all the points for every participant.
        if is_number(row[9]): #the points column must contain a number.
            if int(row[2].partition('/')[0]) == latest_month and abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == latest_year: #cleanup has to be conducted in current month and current year
                if row[0] in participants:
                    participants[row[0]] += float(row[9])
                else:
                    if is_number(row[9]):
                        participants[row[0]] = float(row[9])
#             if abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == latest_year:
            if row[0] in participants_year:
                participants_year[row[0]] += float(row[9])
            else:
                if is_number(row[9]):
                    participants_year[row[0]] = float(row[9])
    participants = sorted(participants.items(), key=lambda x: x[1], reverse=True) #sorts the list of participants from highest points to lowest points.
    participants_year = sorted(participants_year.items(), key=lambda x: x[1], reverse=True)
    first = ''
    second = ''
    third = ''
    first_score = ''
    second_score = ''
    third_score = ''
    first_year = ''
    second_year = ''
    third_year = ''
    first_score_year = ''
    second_score_year = ''
    third_score_year = ''
    if len(participants) >= 1: #first place.
        first = participants[0][0]
        first_score = str(participants[0][1])
    if len(participants) >= 2: #second place.
        second = participants[1][0]
        second_score = str(participants[1][1])
    if len(participants) >= 3: #third place.
        third = participants[2][0]
        third_score = str(participants[2][1])
    if len(participants_year) >= 1:
        first_year = participants_year[0][0]
        first_score_year = str(participants_year[0][1])
    if len(participants_year) >= 2:
        second_year = participants_year[1][0]
        second_score_year = str(participants_year[1][1])
    if len(participants_year) >= 3:
        third_year = participants_year[2][0]
        third_score_year = str(participants_year[2][1])
    place = 4
    rankings_bottom = ''
    rankings_bottom_year = ''
    while place <= len(participants): #generates a row in the rankings table for every participant other than the leading three.
        rankings_bottom += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + '. ' + participants[place - 1][0] + 
                            '</p></div><div class="points"><p><b>' + str(participants[place - 1][1]) + '</b></p></div></div></td></tr>')
        place += 1
    place = 4
    while place <= len(participants_year):
        rankings_bottom_year += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + '. ' + participants_year[place - 1][0] + 
                            '</p></div><div class="points"><p><b>' + str(participants_year[place - 1][1]) + '</b></p></div></div></td></tr>')
        place += 1
    return render_template('ranks.html', first = first, second = second, third = third, first_score = first_score, second_score = second_score, third_score = third_score, rankings_bottom = Markup(rankings_bottom), first_year = first_year, second_year = second_year, third_year = third_year, first_score_year = first_score_year, second_score_year = second_score_year, third_score_year = third_score_year, rankings_bottom_year = Markup(rankings_bottom_year))

@app.route('/ranks-embed')
def render_ranks_embed(): #same as render_ranks() except this renders a page without the top bar and background image.
    data = get_data()
    latest_year = int(datetime.now().strftime('%y'))
    for row in data:
        year = abs(int(row[2].partition('/')[2].partition('/')[2])) % 100
        if year > latest_year:
            latest_year = year
    latest_month = 1
    for row in data:
        if int(row[2].partition('/')[0]) > latest_month and abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == latest_year:
            latest_month = int(row[2].partition('/')[0])
    participants = {}
    participants_year = {}
    for row in data:
        if is_number(row[9]):
            if int(row[2].partition('/')[0]) == latest_month and abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == latest_year: 
                if row[0] in participants:
                    participants[row[0]] += float(row[9])
                else:
                    if is_number(row[9]):
                        participants[row[0]] = float(row[9])
#             if abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == latest_year:
            if row[0] in participants_year:
                participants_year[row[0]] += float(row[9])
            else:
                if is_number(row[9]):
                    participants_year[row[0]] = float(row[9])
    participants = sorted(participants.items(), key=lambda x: x[1], reverse=True) #sorts the list of participants from highest points to lowest points.
    participants_year = sorted(participants_year.items(), key=lambda x: x[1], reverse=True)
    first = ''
    second = ''
    third = ''
    first_score = ''
    second_score = ''
    third_score = ''
    first_year = ''
    second_year = ''
    third_year = ''
    first_score_year = ''
    second_score_year = ''
    third_score_year = ''
    if len(participants) >= 1:
        first = participants[0][0]
        first_score = str(participants[0][1])
    if len(participants) >= 2:
        second = participants[1][0]
        second_score = str(participants[1][1])
    if len(participants) >= 3:
        third = participants[2][0]
        third_score = str(participants[2][1])
    if len(participants_year) >= 1:
        first_year = participants_year[0][0]
        first_score_year = str(participants_year[0][1])
    if len(participants_year) >= 2:
        second_year = participants_year[1][0]
        second_score_year = str(participants_year[1][1])
    if len(participants_year) >= 3:
        third_year = participants_year[2][0]
        third_score_year = str(participants_year[2][1])
    place = 4
    rankings_bottom = ''
    rankings_bottom_year = ''
    while place <= len(participants): 
        rankings_bottom += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + '. ' + participants[place - 1][0] + 
                            '</p></div><div class="points"><p><b>' + str(participants[place - 1][1]) + '</b></p></div></div></td></tr>')
        place += 1
    place = 4
    while place <= len(participants_year):
        rankings_bottom_year += ('<tr><td><div class="rankings-bottom"><div class="name"><p>' + str(place) + '. ' + participants_year[place - 1][0] + 
                            '</p></div><div class="points"><p><b>' + str(participants_year[place - 1][1]) + '</b></p></div></div></td></tr>')
        place += 1
    return render_template('ranks-embed.html', first = first, second = second, third = third, first_score = first_score, second_score = second_score, third_score = third_score, rankings_bottom = Markup(rankings_bottom), first_year = first_year, second_year = second_year, third_year = third_year, first_score_year = first_score_year, second_score_year = second_score_year, third_score_year = third_score_year, rankings_bottom_year = Markup(rankings_bottom_year))

@app.route('/stats')
def render_stats(): #renders the statistics page.
    data = get_data() #gets cleanup data.
    total_trash = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] #lists containing information about the cleanups for every month.
    total_volunteers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_sites = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_cleanups = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_persons = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    coords = []
    month = 1
    chart_data = {}
    end_point = 0.0
    colors = ['#ffb600', '#ff9900', '#ff7900', '#ff5200', '#ff0000']
    index = 0
    for row in data: #checks every cleanup and adds them to the lists of information if they are valid.
        if abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == int(datetime.now().strftime('%Y')) % 100: #only add if the year is the current year.
            if is_number(row[6]) and is_number(row[7]) and is_number(row[1]): #adds to the number of monthly cleanups.
                total_cleanups[row[3] - 1] += 1
            if is_number(row[6]): #adds to the monthly pounds of trash.
                total_trash[row[3] - 1] += float(row[6])
            if is_number(row[7]): #adds to the monthly hours of cleanup time (uses individual time)
                total_time[row[3] - 1] += float(row[7])
            if is_number(row[1]):
                total_volunteers[row[3] - 1] += int(row[1])
            if month != row[3]: #if the month of the cleanup is not the same as the cleanup before it, reset the coordinates list.
                month = row[3]
                coords = []
            if is_number(row[1]):
                total_persons[row[3] - 1] += float(row[1]) #adds to the monthly number of total people involved in cleanups.
                if float(row[1]) <= 1: #assigns a color to each dot on the weight vs time graph, more people involved gives the dot a redder color.
                    index = 0
                elif float(row[1]) <= 5:
                    index = 1
                elif float(row[1]) <= 10:
                    index = 2
                elif float(row[1]) <= 20:
                    index = 3
                else:
                    index = 4
                if is_number(row[6]) and is_number(row[8]): #generates data points for the weight vs time graph.
                    if str(row[1]) in chart_data:
                        chart_data[str(row[1])] = chart_data.get(str(row[1])) +'{ x: ' + str(row[8]) + ', y: ' + str(row[6]) + ', color: "' + colors[index] + '" },'
                    else:
                        chart_data[str(row[1])] = '{ x: ' + str(row[8]) + ', y: ' + str(row[6]) + ', color: "' + colors[index] + '" },'
                    if float(row[8]) > end_point:
                        end_point = float(row[8]) #end point x-coordinate coordinate of the trend line is the same as the point with the greatest time.
            try: #adds the the monthly number of cleanup locations.
                x_coord = float(row[10].partition(',')[0])
                y_coord = float(row[10].partition(',')[2])
                similar = False
                if coords != []: #if coordinates are within 0.00002 of eachother in the x or y direction, then they are considered as cleanups in the same location.
                    for item in coords:
                        item_x = float(item.partition(',')[0])
                        item_y = float(item.partition(',')[2])
                        if item_x > x_coord - 0.002 and item_x < x_coord + 0.002 and item_y > y_coord - 0.002 and item_y < y_coord + 0.002:
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
    counter_group = 1
    chart = ''
    chart_individual = ('{' +
                        'type: "scatter",' +
                        'indexLabelFontSize: 16,' +
                        'name: "Individual",' +
                        'toolTipContent: "<span style=\\"color:#4F81BC \\"><b>{name}</b></span><br/><b> Time: </b> {x} hrs<br/><b> Weight of Trash </b></span> {y} lbs",' +
                        'dataPoints: [')
    chart_group = ''
    trend_line = ''
    trend_line_group = ''
    for key in chart_data: #adds a group of data to the weight vs time graph for every different number of people in a cleanup group. 
        chart_data[key] = chart_data.get(key)[:-1]
        chart += ('{' +
                  'type: "scatter",' +
                  'name: "' + key + ' Person Group",' +
                  'indexLabelFontSize: 16,' +
                  'toolTipContent: "<span style=\\"color:#4F81BC \\"><b>{name}</b></span><br/><b> Time: </b> {x} hrs<br/><b> Weight of Trash </b></span> {y} lbs",' +
                  'dataPoints: [')
        chart += chart_data.get(key)
        chart += ']},'
        if key == '1':
            chart_individual += chart_data.get(key)
            chart_individual += ']},'
        else:
            chart_group += ('{' +
              'type: "scatter",' +
              'name: "' + key + ' Person Group",' +
              'indexLabelFontSize: 16,' +
              'toolTipContent: "<span style=\\"color:#4F81BC \\"><b>{name}</b></span><br/><b> Time: </b> {x} hrs<br/><b> Weight of Trash </b></span> {y} lbs",' +
              'dataPoints: [')
            chart_group += chart_data.get(key)
            chart_group += ']},'
            trend_line_group += 'chart4.data[' + str(counter_group) + '].dataPoints,'
            counter_group += 1
        if counter < len(chart_data): #creates javascript that concats each group of data to calculate the trend line.
            trend_line += 'chart.data[' + str(counter) + '].dataPoints,'
        counter += 1
    chart = chart[:-1]
    chart_group = chart_group[:-1]
    chart_individual = chart_individual[:-1]
    trend_line = trend_line[:-1]
    trend_line_group = trend_line_group.replace(',chart4.data[' + str(counter_group - 1) + '].dataPoints,', '')
    counter = 0
    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
    table = ''
    histogram_weight = ''
    histogram_persons = ''
    histogram_time = ''
    while counter < 12: #calculates averages for histogram and adds them as data, as well as generates the table rows with data for the cumulative cleanup chart.
        if total_trash[counter] != 0.0 and total_volunteers[counter] != 0 and total_sites[counter] != 0:
            table += '<tr><td class="cell no-bold">' + months[counter] + '</td><td class="cell">' + str(total_sites[counter]) + '</td><td class="cell">' + str(total_volunteers[counter]) + '</td><td class="cell">' + str(round(total_trash[counter], 2)) + '</td></tr>' 
        else:
            table += '<tr><td class="cell no-bold">' + months[counter] + '</td><td class="cell"></td><td class="cell"></td><td class="cell"></td></tr>' 
        if total_trash[counter] != 0.0 and total_cleanups[counter] != 0 and total_persons[counter] != 0.0 and total_time[counter] != 0.0:
            histogram_weight += '{ label: "' + months[counter] + '", y: ' + str(total_trash[counter]/total_cleanups[counter]) + ' },'
            histogram_persons += '{ label: "' + months[counter] + '", y: ' + str(total_persons[counter]/total_cleanups[counter]) + ' },'
            histogram_time += '{ label: "' + months[counter] + '", y: ' + str(total_time[counter]/total_cleanups[counter]) + ' },'
        counter += 1
    histogram_weight = histogram_weight[:-1]
    histogram_persons = histogram_persons[:-1]
    histogram_time = histogram_time[:-1]
    return render_template('stats.html', year = datetime.now().strftime('%Y'), table = Markup(table), chart = Markup(chart), chart_group = Markup(chart_group), chart_individual = Markup(chart_individual), trend_line = Markup(trend_line), trend_line_group = Markup(trend_line_group), end_point = Markup(end_point), histogram_weight = Markup(histogram_weight), histogram_persons = Markup(histogram_persons), histogram_time = Markup(histogram_time))

@app.route('/stats-embed')
def render_stats_embed(): #same as render_ranks() except this renders a page without the top bar and background image. It also does not generate data for the charts.
    data = get_data()
    total_trash = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_volunteers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_sites = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    coords = []
    month = 1
    for row in data:
        if abs(int(row[2].partition('/')[2].partition('/')[2])) % 100 == int(datetime.now().strftime('%Y')) % 100:
            if is_number(row[6]):
                total_trash[row[3] - 1] += float(row[6])
            if is_number(row[1]):
                total_volunteers[row[3] - 1] += int(row[1])
            if month != row[3]:
                month = row[3]
                coords = []
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
    counter = 0
    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
    table = ''
    while counter < 12:
        if total_trash[counter] != 0.0 and total_volunteers[counter] != 0 and total_sites[counter] != 0:
            table += '<tr><td class="cell no-bold">' + months[counter] + '</td><td class="cell">' + str(total_sites[counter]) + '</td><td class="cell">' + str(total_volunteers[counter]) + '</td><td class="cell">' + str(round(total_trash[counter], 2)) + '</td></tr>' 
        else:
            table += '<tr><td class="cell no-bold">' + months[counter] + '</td><td class="cell"></td><td class="cell"></td><td class="cell"></td></tr>' 
        counter += 1
    return render_template('stats-embed.html', year = datetime.now().strftime('%Y'), table = Markup(table))

@app.route('/report', methods=['GET', 'POST'])
def report(): #adds a report to the reports sheet.
    if request.method == 'POST':
        wsheet = gsheet.worksheet('Reports')
        data_report = wsheet.get_all_values()
        date_now = datetime.now(tz=pytz.utc)
        date_now = date_now.astimezone(timezone('America/Los_Angeles'))
        try: 
            data_report.append([request.form['location'], request.form['trash'], request.form['comment'], 'Not resolved', date_now.strftime('%m/%d/%Y'), '#DB4437'])
        except:
            data_report.append([request.form['x-location'] + ', ' + request.form['y-location'], request.form['trash'], request.form['comment'], 'Not resolved', date_now.strftime('%m/%d/%Y'), '#DB4437'])
        wsheet.update('A1:G' + str(len(data_report)), data_report)
        cell = wsheet.range('G1:G1')
        cell[0].value = '=GEO_MAP(A1:F' + str(len(data_report)) + ', "reports", "Location")'
        wsheet.update_cells(cell, 'USER_ENTERED')
    if request.form['embed'] == 'true':
        return redirect(url_for('render_maps_embed'))
    return redirect(url_for('render_maps'))

@app.route('/resolve', methods=['GET', 'POST'])
def resolve():
    if request.method == 'POST':
        wsheet = gsheet.worksheet('Resolve Requests')
        data_resolve = wsheet.get_all_values()
        data_resolve.append([request.form['resolve-name'], request.form['resolve-location'], request.form['resolve-date'].replace('-', '/'), request.form['resolve-notes']])
        wsheet.update('A1:G' + str(len(data_resolve)), data_resolve)
    return redirect(url_for('render_maps'))

def is_number(s): #simple way to check if a string is a valid number space on question, check app route, and return post
    try:
        float(s)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run()
