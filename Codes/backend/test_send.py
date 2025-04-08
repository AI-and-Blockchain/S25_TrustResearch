# test_send.py
import requests

url = "http://127.0.0.1:8080/receive-file"
file_path = "uploaded_files.txt"  # ensure this exists from a prior upload

try:
    with open(file_path, "rb") as f:
        response = requests.post(url, files={"uploaded_files": ("uploaded_files.txt", f)})
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("❌ Error:", e)
