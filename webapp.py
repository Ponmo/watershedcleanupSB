from flask import Flask, redirect, Markup, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from flask import render_template
from bson.objectid import ObjectId
from mongosanitizer.sanitizer import sanitize #documentation says used to sanitize user input quieries, but no quieries here are performed with user input.

import pprint
import os
import sys
import pymongo
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

@app.route('/')
def render_layout():
    return render_template('layout.html')
