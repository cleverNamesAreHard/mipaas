# mipaas

## Overview

mipaas is a Flask web application that streamlines the process of mapping fields from customer-uploaded CSV files to various user-provided data formats. It provides a user-friendly interface to facilitate non-technical users in uploading and transforming data according to their requirements.

## Features

1. **Responsive Web Interface**: Designed to be accessible on multiple devices and suited for users with varied technical backgrounds.

2. **Data Format Configuration**: Dynamically load data formats from a JSON configuration file, making it easy to update and add new formats.

3. **CSV File Upload**: Users can upload a CSV file, which is then parsed and displayed in an HTML table on the web page.

4. **Field Mapping**: A web form allows users to manually map CSV fields to predefined fields of the selected target format, including data transformation capabilities.

5. **Data Processing**: After mapping, a 'Process' button triggers the transformation, allowing users to download the processed data.

6. **Error Handling**: Robust error handling mechanisms are in place to guard against data processing errors and enhance the user experience.

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/cleverNamesAreHard/mipaas.git
   cd mipaas
   ```

2. Activate the virtual environment:
	```bash
	# For Unix or MacOS
	source venv/bin/activate

	# For Windows
	venv\Scripts\activate
	```

3. Install the required dependencies:
	```bash
	pip install -r requirements.txt
	```

4. Generate a secret key for Flask:
	```bash
	python -c 'import os; print(os.urandom(16))' 
	```

5. Set up the Flask secret key by adding the following line to your venv/bin/activate script:
	```bash
	export FLASK_SECRET_KEY='your_generated_secret_key_here'
	```

6. Activate the environment variables:
	```bash
	source venv/bin/activate
	```

### Running the Application

1. To start the Flask application in debug mode (internal use only), run:
	```bash
	python app.py
	```
	This will start a development server accessible via http://127.0.0.1:5000 in your web browser.

2. Open your web browser and navigate to http://127.0.0.1:5000 to start using the application.

For internal use, the application has been confirmed to work in Firefox.

### Usage

The application provides a web interface for uploading CSV files, mapping their fields to a predefined format, and validating the structure before loading them into a database.

The field mapping configuration is saved and managed within the application, ensuring that all queries against the uploaded data can be performed consistently.

### Important Notes

The Flask application is currently configured to run in debug mode, which is not recommended for production environments. This setting is for internal use only.

The virtual environment (`venv/`) directory is excluded from the repository for security and privacy reasons. Please ensure that you configure this directories as per the installation guide.
