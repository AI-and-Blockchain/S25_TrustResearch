from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import os
import json

app = Flask(__name__)
CORS(app)

# Connect to Ganache or local Ethereum node
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Load smart contract metadata
with open("contract_data.json", "r") as f:
    contract_data = json.load(f)

contract = web3.eth.contract(
    address=contract_data["address"],
    abi=contract_data["abi"]
)

# ✅ This route is for uploading files (e.g., review_notes.txt)
@app.route('/receive-file', methods=['POST'])
def receive_file():
    print("📥 Received a POST to /receive-file")
    if 'uploaded_files' not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files['uploaded_files']
    os.makedirs("received", exist_ok=True)
    save_path = os.path.join("received", file.filename)
    file.save(save_path)

    print(f"✅ File received and saved at {save_path}")
    return jsonify({"message": "✅ File received successfully!"}), 200

# ✅ This route is for reading IPFS manifest from blockchain
@app.route("/manifest/<user_address>", methods=["GET"])
def get_manifest(user_address):
    if not web3.isAddress(user_address):
        return jsonify({"error": "Invalid Ethereum address"}), 400

    try:
        files = contract.functions.getFiles(user_address).call()
        manifest = []

        for file in files:
            file_name = file[1]
            ipfs_hash = file[0]
            manifest.append(f"{file_name}: {ipfs_hash}")

        return jsonify({
            "message": "✅ Retrieved manifest from blockchain",
            "data": manifest
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Journal Receiver running"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081)
