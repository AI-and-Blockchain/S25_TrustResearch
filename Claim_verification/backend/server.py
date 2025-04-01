import os
import requests
import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from web3 import Web3
from io import BytesIO
import json
app = Flask(__name__)
CORS(app)

# Load contract data
with open("contract_data.json", "r") as f:
    contract_data = json.load(f)

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract = web3.eth.contract(address=contract_data["address"], abi=contract_data["abi"])
web3.eth.defaultAccount = web3.eth.accounts[0]

# IPFS API Endpoint
IPFS_API_URL = "http://127.0.0.1:5001/api/v0"


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'At least one file is required'}), 400

    files = request.files.getlist('files')
    file_details = []

    for file in files:
        file_name = file.filename
        file_path = f"temp/{file_name}"
        file.save(file_path)

        # Upload file to IPFS
        with open(file_path, "rb") as f:
            response = requests.post(f"{IPFS_API_URL}/add", files={"file": f})

        if response.status_code == 200:
            ipfs_hash = response.json()["Hash"]
        else:
            return jsonify({'error': 'Failed to upload to IPFS'}), 500

        os.remove(file_path)

        # Store IPFS hash in Ethereum blockchain
        tx = contract.functions.storeFile(ipfs_hash, file_name).transact({'from': web3.eth.accounts[0]})
        web3.eth.wait_for_transaction_receipt(tx)

        file_details.append(f"{file_name}: {ipfs_hash}")

    # Save to local file (overwriting)
    with open("uploaded_files.txt", "w") as f:
        f.write("\n".join(file_details) + "\n")

    return jsonify({'message': 'Files uploaded successfully!', 'details': file_details})


@app.route('/review-download', methods=['POST'])
def review_download():
    if 'uploaded_files' not in request.files:
        return jsonify({'error': 'Please upload the uploaded_files.txt'}), 400

    uploaded_files = request.files['uploaded_files']

    # Read the uploaded_files.txt to fetch CIDs and filenames
    file_details = uploaded_files.read().decode('utf-8').splitlines()
    downloaded_files = []

    for line in file_details:
        try:
            file_name, ipfs_hash = line.split(": ")
            # Fetch the file from IPFS
            ipfs_url = f"https://ipfs.io/ipfs/{ipfs_hash}"
            response = requests.get(ipfs_url, stream=True)

            if response.status_code == 200:
                file_path = f"temp/{file_name}"
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_files.append(file_path)
                print(f"Downloaded {file_name} to {file_path}")
            else:
                print(f"Failed to download {file_name} from IPFS. Status code: {response.status_code}")
                return jsonify({'error': f'Failed to download file {file_name} from IPFS. Status code: {response.status_code}'}), 500
        except Exception as e:
            print(f"Error processing line: {line}. Exception: {str(e)}")
            return jsonify({'error': f'Error processing line: {line}. Exception: {str(e)}'}), 500

    # Create a ZIP file containing all downloaded files
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in downloaded_files:
            file_name = os.path.basename(file_path)
            zip_file.write(file_path, file_name)
            print(f"Added {file_name} to ZIP file")

    # Clean up downloaded files
    for file_path in downloaded_files:
        os.remove(file_path)
        print(f"Deleted {file_path}")

    # Prepare the ZIP file for download
    zip_buffer.seek(0)
    print("ZIP file created and ready for download")

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='downloaded_files.zip'
    )


if __name__ == '__main__':
    # Create temp directory if it doesn't exist
    if not os.path.exists("temp"):
        os.makedirs("temp")
    app.run(debug=True)