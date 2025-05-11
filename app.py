from flask import Flask, render_template, request, redirect, url_for
import os
import datetime
import gspread
from google.oauth2.service_account import Credentials
from werkzeug.utils import secure_filename
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Google API configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'nota-app-459516-67b2941664a7.json'

SHEET_ID = '1gw0UAP8IaZNrqf5Kkr3GiO4zB53MP7jQFNWG1mOb1Jw'
DRIVE_FOLDER_ID = '1efSC0bJGjBlQ_zRZXT38PZXRuVTx7oUy'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).sheet1

drive_service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(filepath, filename):
    file_metadata = {
        'name': filename,
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(filepath, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded_file.get('id')
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    tanggal = request.form['tanggal']
    keterangan = request.form['keterangan']
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_url = upload_to_drive(filepath, filename)
    else:
        file_url = ''

    sheet.append_row([tanggal, keterangan, file_url])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
