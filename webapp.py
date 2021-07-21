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
credentials = {
    "type": "service_account",
    "project_id": os.environ['project_id'],
    "private_key_id": os.environ['private_key_id'],
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDTMMFIQaGExvVI\nEc2yd44b6iNVQEWD8bNkv44qav0PBQiv4bBnvl/b90Q7Pj+9mq0Jfs2EPKonik3l\nhIwaaUdNsv+97JofnGCbN0iFzhagp0+wcadYhdopJ6YP/dtQzYKbnt1OYMTUw8iP\n9SCLiitzrVp1blEXqYAOCOKFzWEcQc/Gu46zaem3uW0lawOtskGi3dmkStm648A3\ngGZvPxYTeImoUkRp/DcwFmG3vBtSmwwJycYNxDx+VpdbXMd1+JpbsGiQr8JmbBJ/\n8SC4lWLgiEFqvlu8RV1CKh7nzbId14WsPYb/oITnP/BHh2YmvgBir5wVB5J0p36j\n/ZFRsx/DAgMBAAECggEAGz6KaK5izlS2Vs5JKXFH6Wz6kuhgL2XSXThi+DDmJXZi\nSQJF9hQ2nJNY/4WHxod6NCPiEmGbF8+9PdMsGcokEy9404D+3v4W7l8i4XQVMjNz\nUdFPo9lcq/t77ksy7EkexMGpTg+oxMPfD0cxpB62fU1LQqPxHSrWJLlbs6Qrl2/f\n0jtUYNbt3MmUaf+IaEmKktQCqu0ucfEVPl15xZkOLSwPDfwGUmPuSA5w7jUfWEB3\nc84Oq7F76GO6E/O7hFXM8n/VfWHsK/j74QrXid7qgW6PDp46eN7iwH+mLac49fgc\nXyEN80wIh9gKP/Fs9Aef5ER+33AP3yIDMrLvmIVyNQKBgQD8gphVzELX+Krca9Uz\nBvpDA+CQw/i36lCbwEJfNjXgTpm3A1R1t/wNLAtazb9NrtI23aJyES3L98eJagtD\nFGNDehxI1v16fXFyWqBJH6t0rcfKD2/QMmeFWKsFYNN3TV82PtT0Woq/sj8uS4d3\nP2nMuG7RtDFYjJYJLqj+z+XZfQKBgQDWG/eKWa0oMTK2ll8aOKdIz3MWjaGmis82\nOfbxQKv0jgL0b3RX4VXZvp67YHCyhzDl4PA//pTYyFZjDbYfWc6W/UqLZL/Qda8o\nZ11FAbacLNCmrbRXwdfMg+k1raHuOyiO6q2QE1lj5EZp1zB9aqJ2UGLhmtbxjBT2\nFImB6kAiPwKBgQDJkQo/ewVk14i02ZNf31MJCeBKT1WMoovkOK4CyQhq3PORhyP1\nsH+QmDccLh9myIXf7D5PZe0z48Axrif9TRoL9D792jiPffGAgl1u4cwBIPPaFUaB\nYKsIZAZpDajglC/L4o4l3NzjN0t+Dia+By3SkOtNlNTLRbZC8C9Q8O4fFQKBgEIx\nUT0nbj3/v8LtCCfOHgGHiPgO/0vCnD8SeoKpUMABa25wSpKkqmrv4JjjPtQisX5Q\nJVZTeWbvwK1M3uIgXJsXYYVot1hWGbmvAwnDdtYfkL4G87sxxWqH2YBr1qUVCvvs\nF450PO2B9DbifS442lMjlP5UZWE1woE1ZjGQ3xT3AoGAXiYjdRKTeGHe0lc6pFHd\nXG3jvamykBgRuU3udcWXBz1QAoTf5ooxiWtaWz7NAwnXl3ehnI3eEns5kuLPcAV5\nvtFyHmY51Ybut/SG+MzMgfzmvFgwbLfR4K+DlI5PjuhbjaNRpPiOztny4aHST3Ao\nBC4zTUqvIFCRmH6yPmoqK0c=\n-----END PRIVATE KEY-----\n",
    "client_email": os.environ['client_email'],
    "client_id": os.environ['client_id'],
    "auth_uri": os.environ['auth_uri'],
    "token_uri": os.environ['token_uri'],
    "auth_provider_x509_cert_url": os.environ['auth_provider_x509_cert_url'],
    "client_x509_cert_url": os.environ['client_x509_cert_url']
}
#gp = gspread.service_account_from_dict(credentials)
#gsheet = gp.open('Watershed Brigade Clean-up and Point Request Form (Responses)')
#wsheet = gsheet.worksheet('Form Responses 1')

@app.route('/')
def render_layout():
    return render_template('layout.html', data = credentials)
