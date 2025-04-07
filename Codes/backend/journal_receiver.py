# journal_receiver.py
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/receive-file', methods=['POST'])
def receive_file():
    if 'uploaded_files' not in request.files:
        return {"error": "No file found"}, 400

    file = request.files['uploaded_files']
    os.makedirs("received", exist_ok=True)
    save_path = os.path.join("received", file.filename)
    file.save(save_path)

    print(f"✅ File received and saved at {save_path}")
    return {"message": "File received successfully!"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # open to LAN
