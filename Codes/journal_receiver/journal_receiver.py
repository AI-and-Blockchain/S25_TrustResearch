import os
import time
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
from datetime import datetime
import shutil

app = Flask(__name__)
CORS(app)

# Folder setup
RECEIVED_FOLDER = "received"
FEEDBACK_FOLDER = "received_feedback"
os.makedirs(RECEIVED_FOLDER, exist_ok=True)
os.makedirs(FEEDBACK_FOLDER, exist_ok=True)

# Web3 connection
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
web3.eth.defaultAccount = web3.eth.accounts[0]

# Load feedback contract
with open("../backend/feedback_contract_data.json", "r") as f:
    feedback_contract_data = json.load(f)

feedback_contract = web3.eth.contract(
    address=feedback_contract_data["address"],
    abi=feedback_contract_data["abi"]
)

IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"


@app.route("/receive-file", methods=["POST"])
def receive_file():
    if "uploaded_files" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_file = request.files["uploaded_files"]
    original_filename = uploaded_file.filename

    if original_filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Decide folder and standardize naming
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if original_filename == "uploaded_files.txt":
        save_path = os.path.join(RECEIVED_FOLDER, "uploaded_files.txt")
        log_needed = False
    else:
        standardized_name = f"review_notes_{timestamp}.txt"
        save_path = os.path.join(FEEDBACK_FOLDER, standardized_name)
        log_needed = True

    uploaded_file.save(save_path)
    print(f"✅ File received and saved: {save_path}")

    try:
        # Upload to IPFS
        with open(save_path, "rb") as f:
            ipfs_response = requests.post(IPFS_API_URL, files={"file": f})
        if ipfs_response.status_code != 200:
            return jsonify({"error": "Failed to upload to IPFS"}), 500

        ipfs_hash = ipfs_response.json()["Hash"]
        print(f"🧬 Uploaded to IPFS: {ipfs_hash}")

        # Record on blockchain
        tx = feedback_contract.functions.submitFeedback(ipfs_hash, os.path.basename(save_path)).transact({'from': web3.eth.defaultAccount})
        receipt = web3.eth.wait_for_transaction_receipt(tx)
        print(f"🔗 Feedback stored on blockchain (TxHash: {receipt.transactionHash.hex()})")

        # If review comment, also get CID of uploaded_files.txt and save both in a log
        if log_needed:
            uploaded_txt_path = os.path.join(RECEIVED_FOLDER, "uploaded_files.txt")
            if os.path.exists(uploaded_txt_path):
                with open(uploaded_txt_path, "rb") as f:
                    uploaded_ipfs_response = requests.post(IPFS_API_URL, files={"file": f})
                if uploaded_ipfs_response.status_code == 200:
                    uploaded_cid = uploaded_ipfs_response.json()["Hash"]
                    log_path = os.path.join(FEEDBACK_FOLDER, f"review_log_{timestamp}.txt")
                    with open(log_path, "w") as log:
                        log.write(f"uploaded_files.txt: {uploaded_cid}\n")
                        log.write(f"{standardized_name}: {ipfs_hash}\n")
                    print(f"📝 Log saved: {log_path}")
                else:
                    print("⚠️ Could not upload uploaded_files.txt for log.")

        return jsonify({
            "message": "✅ File received, saved, uploaded to IPFS, and tracked on blockchain.",
            "ipfs_hash": ipfs_hash,
            "blockchain_tx": receipt.transactionHash.hex()
        }), 200

    except Exception as e:
        print(f"❌ Error during IPFS or Blockchain operation: {e}")
        return jsonify({"error": f"Internal error: {e}"}), 500




@app.route("/list-accounts", methods=["GET"])
def list_accounts():
    return jsonify(web3.eth.accounts)

@app.route("/assign-reviewer", methods=["POST"])
def assign_reviewer():
    reviewer_address = request.form.get("reviewer_address")
    source_file = "received/uploaded_files.txt"
    
    if not reviewer_address or not os.path.exists(source_file):
        return jsonify({"error": "Missing reviewer address or file"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"manifest_for_{reviewer_address[:6]}_{timestamp}.txt"
    dest_path = os.path.join("assigned_manifests", new_name)
    os.makedirs("assigned_manifests", exist_ok=True)
    shutil.copy(source_file, dest_path)

    print(f"✅ Manifest assigned to reviewer {reviewer_address}: {new_name}")
    return jsonify({"message": f"Reviewer {reviewer_address} assigned successfully!"})

if __name__ == "__main__":
    app.run(port=8081, debug=True)
