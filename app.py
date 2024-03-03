import logging
from flask import Flask, render_template, request, flash, redirect, session, send_from_directory, url_for
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FORMATS_FILE_PATH = 'file_formats.json'

# Load file formats from JSON
with open(FORMATS_FILE_PATH, 'r') as f:
    file_formats = json.load(f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_and_map():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            df = pd.read_csv(filepath)

            session['file_uploaded'] = True
            session['uploaded_filename'] = filename
            session['uploaded_file_headers'] = df.columns.tolist()

            # Convert the first 5 rows of the CSV to a list of dictionaries
            session['first_five_rows'] = df.head(5).to_dict(orient='records')

            flash('File successfully uploaded')
            return redirect(url_for('upload_and_map'))

    if request.method == 'GET':
        if not session.get('file_uploaded'):
            session.clear()

    return render_template('index.html', 
                           file_uploaded=session.get('file_uploaded', False),
                           file_formats=file_formats, 
                           uploaded_file_headers=session.get('uploaded_file_headers', []),
                           first_five_rows=session.get('first_five_rows', []))

@app.route('/submit-mapping', methods=['POST'])
def submit_mapping():
    if 'uploaded_filename' in session and session['file_uploaded']:
        uploaded_filename = session['uploaded_filename']
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_filename)
        df = pd.read_csv(uploaded_file_path)
        
        # Initialize a dictionary to hold the mapping
        mapping = {}
        for header in session['uploaded_file_headers']:
            form_key = 'mapping_' + header.replace(" ", "_").replace(".", "_")
            mapped_field = request.form[form_key]
            # Check if the field is mapped or should retain its original name
            mapping[header] = mapped_field if mapped_field != 'No mapping' else header
        
        # Apply the mapping to rename columns
        df.rename(columns=mapping, inplace=True)

        # Save the modified DataFrame to a new file
        modified_filename = "modified_" + uploaded_filename
        modified_filepath = os.path.join(app.config['UPLOAD_FOLDER'], modified_filename)
        df.to_csv(modified_filepath, index=False)

        # Clear the session and return the modified file to the user
        session.clear()
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=modified_filename, as_attachment=True)

    flash('No file has been uploaded for mapping.')
    return redirect(url_for('upload_and_map'))

@app.route('/downloads/<path:filename>', methods=['GET'])
def download(filename):
    uploads = os.path.join(app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, path=filename, as_attachment=True)

@app.route('/restart', methods=['POST'])
def restart():
    session.clear()
    flash('The process has been restarted.')
    return redirect(url_for('upload_and_map'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run()
