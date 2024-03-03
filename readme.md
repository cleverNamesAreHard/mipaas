# mipaas

## Overview

mipaas (Micro Integration Platform as a Service) is a lightweight Flask application designed to simplify data integration workflows. This tool enables users to effortlessly map fields from customer-uploaded CSV files to specified data formats, streamlining the data preparation process for various analytics or database loading tasks. With its intuitive interface, mipaas is accessible to both technical and non-technical users, allowing for easy data uploading and transformation to meet diverse requirements. Whether you're consolidating data for analysis, preparing datasets for database ingestion, or integrating information across systems, mipaas serves as an easy tool for efficient and accurate data handling.

![User Interface](https://i.imgur.com/J6dLtaO.png)

## Features

1. **Responsive Web Interface**: Designed to be accessible on multiple devices and suited for users with varied technical backgrounds.

2. **Data Format Configuration**: Dynamically load data formats from a JSON configuration file, making it easy to update and add new formats.

3. **CSV File Upload**: Users can upload a CSV file, which is then parsed and displayed in an HTML table on the web page.

4. **Field Mapping**: A web form allows users to manually map CSV fields to predefined fields of the selected target format, including data transformation capabilities.

5. **Data Processing**: After mapping, a 'Process' button triggers the transformation, allowing users to download the processed data.

6. **Error Handling**: Robust error handling mechanisms are in place to guard against data processing errors and enhance the user experience.

7. **Command-Line Interface (CLI):** For users seeking to automate data transformation tasks, mipaas now includes a CLI tool. This feature allows for the processing of files through the command line, making it a powerful addition for batch processing or integration into automated workflows. Note: The Flask server must be running for the CLI to function.

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
	python -c "import os; print(os.urandom(8).hex())" 
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

### Using the CLI
To use the CLI for automated file transformation, ensure the Flask server is running and then use the `mipaas.py` script as follows:
```bash
python mipaas.py <input_file_location> <file_mapping_location> <output_file_location>
```

To create the mapping file, you must use the web interface to specify the field mapping, and select "Export".

### Adding Data Formats

1. In `file_formats.json`, add a comma at the end of the line containing `"Account File"`

2. In quotes, add a name for the new format, and add the list:
    ```json
    "Account File": ["data", "fields", "here"],
    "My New File Format": []
    ```

3. Add the fields you require 

### Usage

The application provides a web interface for uploading CSV files, mapping their fields to a predefined format, and validating the structure before loading them into a database.

The field mapping configuration is saved and managed within the application, ensuring that all queries against the uploaded data can be performed consistently.

### Important Notes

The Flask application is currently configured to run in debug mode, which is not recommended for production environments. This setting is for internal use only.

The virtual environment (`venv/`) directory is excluded from the repository for security and privacy reasons. Please ensure that you configure this directories as per the installation guide.
