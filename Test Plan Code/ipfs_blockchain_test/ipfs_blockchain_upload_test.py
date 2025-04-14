import os
import json
import requests
from web3 import Web3

# === CONFIGURATION ===
IPFS_API_URL = "http://127.0.0.1:5001/api/v0"
GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_JSON_PATH = "ipfs_ganache_deploy code/blockchain/build/contracts/FileStorage.json"
UPLOAD_DIR = "Files to upload"
MANIFEST_PATH = "uploaded_manifest.txt"

# === Load contract data ===
with open(CONTRACT_JSON_PATH) as f:
    contract_json = json.load(f)

networks = contract_json.get("networks", {})
if not networks:
    raise ValueError("❌ No deployed contract networks found.")

network_id = list(networks.keys())[0]
contract_address = networks[network_id]["address"]
abi = contract_json["abi"]

with open("contract_data.json", "w") as f:
    json.dump({"address": contract_address, "abi": abi}, f, indent=2)

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
contract = web3.eth.contract(address=contract_address, abi=abi)
web3.eth.defaultAccount = web3.eth.accounts[0]

# === Upload files and store CIDs ===
if not os.path.isdir(UPLOAD_DIR):
    raise FileNotFoundError(f"❌ Folder '{UPLOAD_DIR}' not found.")

print(f"\n📁 Uploading files from '{UPLOAD_DIR}'...\n")
file_records = []

for file_name in os.listdir(UPLOAD_DIR):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.isfile(file_path):
        continue

    print(f"📤 Uploading {file_name} to IPFS...")
    with open(file_path, "rb") as file:
        response = requests.post(f"{IPFS_API_URL}/add", files={"file": file})

    if response.status_code == 200:
        ipfs_hash = response.json()["Hash"]
        print(f"✅ Uploaded. IPFS Hash: {ipfs_hash}")
    else:
        print(f"❌ Failed to upload {file_name}")
        continue

    contract.functions.storeFile(ipfs_hash, file_name).transact({'from': web3.eth.defaultAccount})
    file_records.append(f"{file_name}: {ipfs_hash}")

# === Write manifest ===
with open(MANIFEST_PATH, "w") as f:
    f.write("\n".join(file_records))
print(f"\n📝 CID manifest written to {MANIFEST_PATH}")
