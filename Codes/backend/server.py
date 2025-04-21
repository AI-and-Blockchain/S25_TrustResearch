import os
import sys
import time
import requests
import subprocess
import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from web3 import Web3
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from citation_graph.citationGraphEvaluator import CitationGraphEvaluator
from citation_graph.citationFraudDetector import CitationFraudDetector  # Already used inside



app = Flask(__name__)
CORS(app)

# create citationGraphEvaluator object
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
relative_path = "../citation_graph/model.pth"
model_path = os.path.join(current_directory, relative_path)
citationEvaluator = CitationGraphEvaluator(model_path)




# Load smart contract metadata
with open("contract_data.json", "r") as f:
    contract_data = json.load(f)

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract = web3.eth.contract(address=contract_data["address"], abi=contract_data["abi"])
web3.eth.defaultAccount = web3.eth.accounts[0]
#IPFS_GATEWAY = "https://ipfs.io/ipfs"
IPFS_GATEWAY = "http://127.0.0.1:8080/ipfs"  # local IPFS gateway


def download_files_from_manifest(lines):
    os.makedirs("temp", exist_ok=True)
    download_manifest = []

    for line in lines:
        try:
            file_name, cid = line.strip().split(": ")
            url = f"{IPFS_GATEWAY}/{cid.strip()}"
            path = os.path.join("temp", file_name)
            download_manifest.append((file_name, url, path))

            response = requests.get(url, stream=True, timeout=300)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
            else:
                raise Exception(f"Failed to download {file_name} (HTTP {response.status_code})")

        except Exception as e:
            raise Exception(f"Error downloading {file_name}: {str(e)}")

    def file_fully_written(path):
        size1 = os.path.getsize(path)
        time.sleep(1.5)
        size2 = os.path.getsize(path)
        return size1 == size2 and size1 > 0

    waited = 0
    max_wait = 100
    interval = 3
    ready = False

    while waited < max_wait:
        not_ready = []
        for _, _, path in download_manifest:
            if not os.path.exists(path) or not file_fully_written(path):
                not_ready.append(path)
        if not not_ready:
            ready = True
            break
        print(f"⏳ Waiting for files to complete: {', '.join(not_ready)}")
        time.sleep(interval)
        waited += interval

    if not ready:
        raise Exception(f"Timeout: Some files are still being written: {', '.join(not_ready)}")

    return download_manifest


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'At least one file is required'}), 400

    files = request.files.getlist('files')
    file_details = []
    os.makedirs("temp", exist_ok=True)

    trig_path = None
    file_map = {}  # {filename: full_path}

    # Step 1: Save all uploaded files locally and detect .trig
    for file in files:
        file_name = file.filename
        file_path = os.path.join("temp", file_name)
        file.save(file_path)
        file_map[file_name] = file_path
        if file_name.endswith(".trig"):
            trig_path = file_path

    
    
    # ============================ #
    # ✅ Citation Score Evaluation #
    # ============================ #
    if trig_path:
        try:
            import rdflib
            g = rdflib.ConjunctiveGraph()
            g.parse(trig_path, format="trig")

            from rdflib.namespace import DCTERMS
            from rdflib import Namespace

            ex = Namespace("http://example.org/")
            cito = Namespace("http://purl.org/spar/cito/")

            paper_uri = ex.paperA
            title = "Title not available"
            authors = []
            references = []

            # ✅ Extract authors
            for s, p, o in g.triples((paper_uri, DCTERMS.creator, None)):
                authors.append(str(o))

            # ✅ Extract literal references directly (DOI, arXiv, etc.)
            for s, p, o in g.triples((paper_uri, cito.cites, None)):
                references.append(str(o))

            paperDetails = {
                "title": title,
                "authors": authors,
                "references": references
            }

            citation_score = citationEvaluator.evaluateGraph(paperDetails)
            if citation_score is not None:
                score_text_path = os.path.join("temp", "citation_score.txt")
                with open(score_text_path, "w") as f:
                    f.write(f"Citation Fraud Score: {round(citation_score * 100, 2)}%\n")

                # Upload score file to IPFS
                with open(score_text_path, "rb") as f:
                    response = requests.post("http://127.0.0.1:5001/api/v0/add", files={"file": f})
                if response.status_code == 200:
                    ipfs_hash = response.json()["Hash"]
                    tx = contract.functions.storeFile(ipfs_hash, "citation_score.txt").transact({'from': web3.eth.accounts[0]})
                    web3.eth.wait_for_transaction_receipt(tx)
                    file_details.append(f"citation_score.txt: {ipfs_hash}")

                print(f"✅ Citation fraud score saved: {citation_score}")

        except Exception as e:
            print(f"❌ Error during citation fraud analysis: {e}")



    
    
    
    
    
    
    
    # Step 3: Upload all files to IPFS and store on blockchain
    for file_name, file_path in file_map.items():
        with open(file_path, "rb") as f:
            response = requests.post("http://127.0.0.1:5001/api/v0/add", files={"file": f})
        if response.status_code == 200:
            ipfs_hash = response.json()["Hash"]
        else:
            return jsonify({'error': f'Failed to upload {file_name} to IPFS'}), 500

        tx = contract.functions.storeFile(ipfs_hash, file_name).transact({'from': web3.eth.accounts[0]})
        web3.eth.wait_for_transaction_receipt(tx)
        file_details.append(f"{file_name}: {ipfs_hash}")
    file_details.sort(key=lambda x: x.startswith("citation_score.txt"))

    # Step 4: Write manifest (uploaded_files.txt)
    uploaded_file_path = "uploaded_files.txt"
    with open(uploaded_file_path, "w") as f:
        f.write("\n".join(file_details) + "\n")

    # Step 5: Send to journal authority
    DESTINATION_URL = "http://127.0.0.1:8081/receive-file"
    try:
        with open(uploaded_file_path, "rb") as file_to_send:
            response = requests.post(DESTINATION_URL, files={"uploaded_files": ("uploaded_files.txt", file_to_send)})
        if response.status_code == 200:
            print("✅ File successfully sent to journal authority at", DESTINATION_URL)
        else:
            print(f"⚠️ Failed to send file. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending file to remote journal authority: {e}")

    return jsonify({'message': 'Files uploaded successfully!', 'details': file_details}), 200




@app.route("/review-validate", methods=["POST"])
def review_validate():
    import shutil

    # Clear temp/ before starting
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.makedirs("temp", exist_ok=True)

    
    if 'uploaded_files' not in request.files:
        return jsonify({"error": "Please upload uploaded_files.txt"}), 400

    uploaded = request.files['uploaded_files']
    lines = uploaded.read().decode().splitlines()

    try:
        download_manifest = download_files_from_manifest(lines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

        return jsonify({"output": result.stdout.strip() or "✅ Validation completed but script did not return any output."})

    except Exception as e:
        return jsonify({"error": f"Error running reviewer_validation_script.py: {e}"}), 500


@app.route("/review-download", methods=["POST"])
def review_download():
    if 'uploaded_files' not in request.files:
        return jsonify({"error": "Please upload uploaded_files.txt"}), 400

    uploaded = request.files['uploaded_files']
    lines = uploaded.read().decode().splitlines()

    try:
        download_manifest = download_files_from_manifest(lines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    zip_path = os.path.join("temp", "downloaded_files.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for _, _, path in download_manifest:
            zipf.write(path, os.path.basename(path))

    return send_file(zip_path, as_attachment=True, download_name="review_package.zip")


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    app.run(debug=True, use_reloader=False)
