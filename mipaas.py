import requests
import sys
import os

def file_exists(filepath):
    """Check if a file exists and is accessible."""
    return os.path.exists(filepath)

def main(input_file, mapping_file, output_file):
    # Validate files exist
    for file_path in [input_file, mapping_file]:
        if not file_exists(file_path):
            print(f"Error: The file {file_path} does not exist or is not accessible.")
            sys.exit(1)

    # URL of the Flask endpoint
    url = 'http://127.0.0.1:5000/process-file-mapping'
    
    # Prepare the JSON payload
    payload = {
        'input_file': input_file,
        'mapping_file': mapping_file,
        'output_file': output_file
    }
    
    # Make the POST request
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            print("Success:", response_data.get('message'))
            print("Output file:", response_data.get('output_file'))
        else:
            print("Error:", response_data.get('error'))
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python mipaas.py <input_file_location> <file_mapping_location> <output_file_location>")
        sys.exit(1)

    input_file_location = sys.argv[1]
    file_mapping_location = sys.argv[2]
    output_file_location = sys.argv[3]
    
    main(input_file_location, file_mapping_location, output_file_location)
