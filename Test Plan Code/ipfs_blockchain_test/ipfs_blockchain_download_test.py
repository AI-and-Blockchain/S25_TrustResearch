import os
import requests

# === CONFIGURATION ===
IPFS_GATEWAY = "https://ipfs.io/ipfs"
MANIFEST_PATH = "uploaded_manifest.txt"
DOWNLOAD_DIR = "Downloaded_Files"

# === Read uploaded manifest ===
if not os.path.exists(MANIFEST_PATH):
    raise FileNotFoundError(f"❌ {MANIFEST_PATH} not found.")

with open(MANIFEST_PATH, "r") as f:
    entries = [line.strip() for line in f.readlines() if ": " in line]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === Download files ===
print(f"\n📥 Downloading files to '{DOWNLOAD_DIR}'...\n")
for entry in entries:
    try:
        file_name, cid = entry.split(": ")
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        url = f"{IPFS_GATEWAY}/{cid.strip()}"

        print(f"⬇️  Downloading {file_name} from {cid}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Saved: {file_path}")
        else:
            print(f"❌ Failed to download {file_name} (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error processing '{entry}': {e}")

print("\n🎉 All downloads complete.")
