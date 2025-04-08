from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/receive-file', methods=['POST'])
def receive_file():
    print("📥 Received a POST to /receive-file")  # ADD THIS
    if 'uploaded_files' not in request.files:
        return {"error": "No file found"}, 400

    file = request.files['uploaded_files']
    os.makedirs("received", exist_ok=True)
    save_path = os.path.join("received", file.filename)
    file.save(save_path)

    print(f"✅ File received and saved at {save_path}")
    return {"message": "File received successfully!"}, 200

@app.route("/")
def home():
    return "✅ Hello from Journal Receiver!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)

