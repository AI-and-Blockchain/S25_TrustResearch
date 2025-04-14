import os
import subprocess

# ===== CONFIGURATION =====
MANIFEST_PATH = "uploaded_manifest.txt"           # The manifest file with filename: CID
DESTINATION_DIR = "Downloaded_Files"       # Where to store downloaded files
IPFS_GET_COMMAND = "ipfs get"                  # Ensure `ipfs` CLI is in PATH

# ===== ENSURE DESTINATION DIR EXISTS =====
os.makedirs(DESTINATION_DIR, exist_ok=True)

# ===== READ MANIFEST AND DOWNLOAD FILES =====
with open(MANIFEST_PATH, "r") as f:
    lines = f.read().splitlines()

for line in lines:
    try:
        filename, cid = line.split(": ")
        print(f"⬇️  Downloading {filename} from {cid} ...")

        # Run: ipfs get <CID> -o <DESTINATION_DIR>/<filename>
        output_path = os.path.join(DESTINATION_DIR, filename)
        result = subprocess.run(
            ["ipfs", "get", cid.strip(), "-o", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Downloaded {filename} successfully!\n")
        else:
            print(f"❌ Failed to download {filename}")
            print(result.stderr)

    except Exception as e:
        print(f"⚠️ Error processing line '{line}': {e}")
