from flask import Flask, request, jsonify, send_from_directory, flash, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
from xml.dom import minidom
from xml.sax.saxutils import escape
import pandas as pd
import json
import logging
import os
import re
import xml.etree.ElementTree as ET


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super-secret-key') # Default if not set
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FORMATS_FILE_PATH = 'file_formats.json'

# Load file formats from JSON
with open(FORMATS_FILE_PATH, 'r') as f:
    file_formats = json.load(f)

def allowed_file(filename):
    logging.debug(f"Checking if {filename} is allowed")
    allowed = '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS
    logging.debug(f"Allowed: {allowed}")
    return allowed

import xml.etree.ElementTree as ET
import pandas as pd
import logging

def xml_to_dataframe(xml_content_or_path, is_path=True):
    logging.debug("Starting conversion from XML to DataFrame.")
    
    try:
        # Determine the source of the XML (file path or XML string) and parse it
        if is_path:
            logging.debug(f"Parsing XML from file path: {xml_content_or_path}")
            tree = ET.parse(xml_content_or_path)
        else:
            logging.debug("Parsing XML from string.")
            tree = ET.ElementTree(ET.fromstring(xml_content_or_path))
        
        root = tree.getroot()
        logging.debug(f"Root element of the XML: {root.tag}")

        data = []
        # Check if the root has children and process accordingly
        if len(root) > 0 and all(child.tag == root[0].tag for child in root[1:]):
            logging.debug("Processing multiple records in XML.")
            for child in root:
                record = {elem.tag: elem.text for elem in child}
                logging.debug(f"Processed record: {record}")
                data.append(record)
        else:
            logging.debug("Processing a single record in XML.")
            record = {child.tag: child.text for child in root}
            logging.debug(f"Processed record: {record}")
            data.append(record)
        
        df = pd.DataFrame(data)
        logging.debug(f"DataFrame columns: {df.columns.tolist()}")
        logging.debug(f"First few rows of the DataFrame:\n{df.head()}")
        return df
    except ET.ParseError as pe:
        logging.error(f"XML parsing error: {pe}")
        raise
    except Exception as e:
        logging.error(f"General error converting XML to DataFrame: {e}")
        raise

import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.sax.saxutils import escape
import logging

def dynamic_dataframe_to_xml_file(df, xml_input_location, xml_output_location, mapping):
    logging.debug("Starting conversion from DataFrame to XML.")
    
    try:
        logging.debug(f"Input XML for structure reference: {xml_input_location}")
        tree = ET.parse(xml_input_location)
        root = tree.getroot()
        
        logging.debug(f"Root element found in the input XML: {root.tag}")
        output_root = ET.Element(root.tag)
        
        row_counter = 0
        for _, row in df.iterrows():
            row_counter += 1
            child_tag = root[0].tag if len(root) > 0 else 'record'
            child_elem = ET.SubElement(output_root, child_tag)
            
            logging.debug(f"Processing row {row_counter} into XML tag: {child_tag}")
            for original_tag, new_tag in mapping.items():
                if new_tag != "No mapping" and new_tag in row:
                    element_text = escape(str(row[new_tag]))
                    sub_elem = ET.SubElement(child_elem, original_tag if original_tag in df.columns else new_tag)
                    sub_elem.text = element_text
                    logging.debug(f"Added XML element: <{original_tag if original_tag in df.columns else new_tag}>{element_text}</{original_tag if original_tag in df.columns else new_tag}>")

        xml_str = ET.tostring(output_root, encoding='unicode')
        xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
        with open(xml_output_location, 'w') as f:
            f.write(xml_pretty_str)
        
        logging.debug(f"XML file successfully written to {xml_output_location}. Total rows processed: {row_counter}.")
    except Exception as e:
        logging.error(f"Error during DataFrame to XML conversion: {e}")
        raise

@app.route('/submit-mapping', methods=['POST'])
def submit_mapping():
    logging.debug("Submit mapping request received.")
    
    if 'uploaded_filename' in session and session['file_uploaded']:
        uploaded_filename = session['uploaded_filename']
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_filename)
        logging.info(f"Processing mapping for uploaded file: {uploaded_filename}")
        
        # Load the uploaded file into a DataFrame
        try:
            if uploaded_filename.endswith('.csv'):
                logging.debug("Loading CSV file into DataFrame.")
                df = pd.read_csv(uploaded_file_path)
            elif uploaded_filename.endswith('.xml'):
                logging.debug("Loading XML file into DataFrame.")
                df = xml_to_dataframe(uploaded_file_path)
            else:
                logging.warning(f"Unsupported file format for {uploaded_filename}.")
                flash('Unsupported file format.')
                return redirect(url_for('upload_and_map'))

        except Exception as e:
            logging.error(f"Error loading file into DataFrame: {e}")
            flash("Error processing the file.")
            return redirect(url_for('upload_and_map'))

        # Initialize and apply field mappings from the form
        mapping = {}
        for header in session['uploaded_file_headers']:
            form_key = 'mapping_' + header.replace(" ", "_").replace(".", "_")
            mapped_field = request.form.get(form_key)
            mapping[header] = mapped_field if mapped_field != 'No mapping' else None
        
        for column, mapped_column in mapping.items():
            if mapped_column and column in df.columns:
                logging.debug(f"Applying mapping: {column} to {mapped_column}")
                df.rename(columns={column: mapped_column}, inplace=True)

        # Determine output format and construct modified filename
        save_as_csv = "saveAsCSV" in request.form or uploaded_filename.endswith('.csv')
        file_extension = 'csv' if save_as_csv else 'xml'
        modified_filename = f"modified_{uploaded_filename.rsplit('.', 1)[0]}.{file_extension}"
        modified_filepath = os.path.join(app.config['UPLOAD_FOLDER'], modified_filename)
        logging.debug(f"Modified file path: {modified_filepath}")

        # Save the modified DataFrame in the chosen format
        try:
            if save_as_csv:
                logging.info("Saving modified DataFrame as CSV.")
                df.to_csv(modified_filepath, index=False)
            else:
                logging.info("Converting modified DataFrame to XML.")
                dynamic_dataframe_to_xml_file(df, uploaded_file_path, modified_filepath, mapping)
            logging.info("File modification and saving completed successfully.")
        except Exception as e:
            logging.error(f"Error saving modified file: {e}")
            flash("Error saving the modified file.")
            return redirect(url_for('upload_and_map'))

        # Clear session and offer download
        session.clear()
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=modified_filename, as_attachment=True)

    else:
        logging.warning("No file has been uploaded for mapping.")
        flash('No file has been uploaded for mapping.')
        return redirect(url_for('upload_and_map'))

@app.route('/', methods=['GET', 'POST'])
def upload_and_map():
    logging.debug("Accessed the upload and map page.")
    
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logging.info(f"File saved: {filepath}")
            
            # Determine if the file is CSV or XML and load accordingly
            file_type = 'csv' if filename.endswith('.csv') else 'xml'
            logging.debug(f"Determined file type: {file_type}")
            
            try:
                if file_type == 'csv':
                    logging.debug("Loading CSV file into DataFrame.")
                    df = pd.read_csv(filepath)
                else:
                    logging.debug("Loading XML file into DataFrame.")
                    df = xml_to_dataframe(filepath)
            except Exception as e:
                logging.error(f"Error loading file into DataFrame: {e}")
                flash("Error processing the file.")
                return redirect(url_for('upload_and_map'))

            # Setting variables in session
            session['file_uploaded'] = True
            session['uploaded_filename'] = filename
            session['uploaded_file_headers'] = df.columns.tolist()
            session['uploaded_file_type'] = file_type
            
            # Convert the first 5 rows of the DataFrame to a list of dictionaries for preview
            session['first_five_rows'] = df.head(5).to_dict(orient='records')
            logging.debug("File preview generated.")
            
            flash('File successfully uploaded')
        else:
            logging.warning("File not allowed or missing.")
            flash('Invalid file format or no file was uploaded.')
            
        return redirect(url_for('upload_and_map'))
    
    if request.method == 'GET':
        # Clear session if it's a new GET request indicating a fresh start
        if not session.get('file_uploaded'):
            logging.debug("Clearing session for new file upload.")
            session.clear()
    
    logging.debug("Rendering the upload and map page.")
    return render_template('index.html', 
                           file_uploaded=session.get('file_uploaded', False),
                           uploaded_file_type=session.get('uploaded_file_type', ''),
                           file_formats=file_formats, 
                           uploaded_file_headers=session.get('uploaded_file_headers', []),
                           first_five_rows=session.get('first_five_rows', []))

@app.route('/downloads/<path:filename>', methods=['GET'])
def download(filename):
    logging.debug(f"Download request received for file: {filename}")

    # Define the directory where uploads are stored
    uploads = os.path.join(app.config['UPLOAD_FOLDER'])
    file_path = os.path.join(uploads, filename)

    # Check if the file exists in the uploads directory
    if not os.path.exists(file_path):
        logging.error(f"File not found for download: {file_path}")
        return "File not found.", 404

    logging.info(f"Initiating download for file: {file_path}")

    try:
        # Attempt to send the file from the server to the client
        response = send_from_directory(directory=uploads, path=filename, as_attachment=True)
        logging.info(f"File successfully sent for download: {filename}")
        return response
    except Exception as e:
        logging.error(f"Error during file download: {e}")
        return "An error occurred during file download.", 500

@app.route('/restart', methods=['POST'])
def restart():
    logging.debug("Restart request received.")

    try:
        # Attempting to clear the session
        session.clear()
        logging.info("Session has been cleared successfully.")

        # Flashing a message to the user about the restart
        flash('The process has been restarted.')

        # Redirecting back to the upload and map page
        response = redirect(url_for('upload_and_map'))
        logging.info("Redirecting to the upload and map page.")

        return response
    except Exception as e:
        # Log any exceptions that occur during the restart process
        logging.error(f"Error during restart: {e}")
        flash('An error occurred during restart.')
        # Even if an error occurs, attempt to redirect the user back
        return redirect(url_for('upload_and_map'))

@app.route('/process-file-mapping', methods=['POST'])
def process_file_mapping():
    logging.debug("Starting file processing")

    # Validate file parts in the request
    if 'input_file' not in request.files or 'mapping_file' not in request.files:
        logging.error("Missing file part in the request")
        return jsonify({'error': 'No file part in the request'}), 400

    input_file = request.files['input_file']
    mapping_file = request.files['mapping_file']
    output_file_name = request.form.get('output_file', '')
    output_as_csv = request.form.get('output_as_csv', 'false').lower() == 'true'

    if not output_file_name:
        logging.error("Output file name not provided")
        return jsonify({'error': 'Output file name not provided'}), 400

    input_file_path = os.path.join(UPLOAD_FOLDER, secure_filename(input_file.filename))
    output_file_path = os.path.join(UPLOAD_FOLDER, secure_filename(output_file_name))

    # Temporary save for processing
    input_file.save(input_file_path)

    try:
        mapping_dict = json.load(mapping_file)
        logging.debug(f"Loaded mapping: {mapping_dict}")

        if input_file.filename.endswith('.csv'):
            logging.debug("Processing a CSV file")
            df = pd.read_csv(input_file_path)
            logging.debug(f"DataFrame from CSV: \n{df.head()}")

            # Apply mapping
            df.rename(columns={k: v for k, v in mapping_dict.items() if v != "No mapping"}, inplace=True)

            if output_as_csv:
                logging.debug("Saving as CSV")
                df.to_csv(output_file_path, index=False)
            else:
                logging.debug("Converting CSV to XML with mapping")
                # Ensure dynamic_dataframe_to_xml_file is designed to handle CSV data correctly
                dynamic_dataframe_to_xml_file(df, input_file_path, output_file_path, mapping_dict)
        else:
            # Handle XML processing if needed
            pass

        logging.debug("File processing completed successfully")
        return jsonify({'message': 'File processed successfully', 'output_file': output_file_name}), 200
    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
            logging.debug("Temporarily saved input file removed")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)