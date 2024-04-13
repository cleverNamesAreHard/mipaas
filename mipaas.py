import requests
import argparse

def main(args):
    # URL of the Flask endpoint
    url = 'http://127.0.0.1:5000/process-file-mapping'

    # Prepare the files for uploading
    with open(args.input_file, 'rb') as input_f, open(args.mapping_file, 'rb') as mapping_f:
        files = {
            'input_file': input_f,
            'mapping_file': mapping_f
        }
        data = {
            'output_file': args.output_file,
            'output_as_csv': args.output_csv
        }
        
        # Make the POST request with files and form data
        response = requests.post(url, files=files, data=data)
        
        # Process the response
        if response.status_code == 200:
            print("Success:", response.json().get('message'))
        else:
            print("Error:", response.status_code, response.text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process file mappings.')
    parser.add_argument('input_file', help='Input file location')
    parser.add_argument('mapping_file', help='File mapping location')
    parser.add_argument('output_file', help='Output file location')
    parser.add_argument('--output-csv', action='store_true', help='Flag to output as CSV (for XML inputs)', default=False)

    args = parser.parse_args()
    main(args)
