import os
import time
import requests
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json

app = Flask(__name__)
CORS(app)

# Load smart contract metadata
with open("contract_data.json", "r") as f:
    contract_data = json.load(f)

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract = web3.eth.contract(address=contract_data["address"], abi=contract_data["abi"])
web3.eth.defaultAccount = web3.eth.accounts[0]
IPFS_GATEWAY = "https://ipfs.io/ipfs"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'At least one file is required'}), 400

    files = request.files.getlist('files')
    file_details = []

    os.makedirs("temp", exist_ok=True)

    for file in files:
        file_name = file.filename
        file_path = os.path.join("temp", file_name)
        file.save(file_path)

        with open(file_path, "rb") as f:
            response = requests.post("http://127.0.0.1:5001/api/v0/add", files={"file": f})
        if response.status_code == 200:
            ipfs_hash = response.json()["Hash"]
        else:
            return jsonify({'error': f'Failed to upload {file_name} to IPFS'}), 500

        tx = contract.functions.storeFile(ipfs_hash, file_name).transact({'from': web3.eth.accounts[0]})
        web3.eth.wait_for_transaction_receipt(tx)
        file_details.append(f"{file_name}: {ipfs_hash}")

    # Write the uploaded_files.txt file
    uploaded_file_path = "uploaded_files.txt"
    with open(uploaded_file_path, "w") as f:
        f.write("\n".join(file_details) + "\n")

    # SEND FILE TO REMOTE IP ADDRESS
    DESTINATION_URL = "http://127.0.0.1:8081/receive-file"  # use the working IP

    try:
        with open(uploaded_file_path, "rb") as file_to_send:
            response = requests.post(
                DESTINATION_URL,
                files={"uploaded_files": ("uploaded_files.txt", file_to_send)},
            )
        if response.status_code == 200:
            print("✅ File successfully sent to journal authority at", DESTINATION_URL)
        else:
            print(f"⚠️ Failed to send file. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending file to remote journal authority: {e}")

    return jsonify({'message': 'Files uploaded successfully!', 'details': file_details}), 200



@app.route("/review-validate", methods=["POST"])
def review_validate():
    if 'uploaded_files' not in request.files:
        return jsonify({"error": "Please upload uploaded_files.txt"}), 400

    uploaded = request.files['uploaded_files']
    lines = uploaded.read().decode().splitlines()

    os.makedirs("temp", exist_ok=True)
    download_manifest = []

    for line in lines:
        try:
            file_name, cid = line.strip().split(": ")
            url = f"{IPFS_GATEWAY}/{cid.strip()}"
            path = os.path.join("temp", file_name)
            download_manifest.append((file_name, url, path))

            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
            else:
                print(f"❌ Initial download failed for {file_name}")
        except Exception as e:
            return jsonify({"error": f"Error while downloading {file_name}: {str(e)}"}), 500

    # Wait until all files exist and are stable in size
    def file_fully_written(path):
        size1 = os.path.getsize(path)
        time.sleep(1)
        size2 = os.path.getsize(path)
        return size1 == size2 and size1 > 0

    waited = 0
    max_wait = 15
    interval = 2
    ready = False

    while waited < max_wait:
        not_ready = []
        for _, _, path in download_manifest:
            if not os.path.exists(path) or not file_fully_written(path):
                not_ready.append(path)
        if not not_ready:
            ready = True
            break
        print(f"⏳ Waiting for files to finish writing: {', '.join(not_ready)}")
        time.sleep(interval)
        waited += interval

    if not ready:
        return jsonify({
            "error": f"Timeout: The following files are incomplete or still writing: {', '.join(not_ready)}"
        }), 500

    # Run the validation script
    try:
        result = subprocess.run(
            ["python", "-u", "reviewer_validation_script.py"],
            cwd="temp",
            capture_output=True,
            text=True,
            timeout=60
        )


        print("======== STDOUT ========")
        print(result.stdout)
        print("======== STDERR ========")
        print(result.stderr)

        if result.returncode != 0:
            return jsonify({
                "error": f"❌ Script failed with return code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout
            }), 500

        if not result.stdout.strip():
            return jsonify({
                "error": "✅ Validation completed but script did not return any output.",
                "stderr": result.stderr
            }), 200

        return jsonify({"output": result.stdout})

    except Exception as e:
        return jsonify({"error": f"Error running reviewer_validation_script.py: {e}"}), 500


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    app.run(debug=True, use_reloader=False)
