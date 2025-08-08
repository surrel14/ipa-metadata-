import zipfile
import plistlib
import json
import os
import sys

def extract_metadata_from_ipa(ipa_path):
    if not os.path.isfile(ipa_path):
        raise FileNotFoundError(f"IPA file not found: {ipa_path}")

    with zipfile.ZipFile(ipa_path, 'r') as ipa:
        # Locate Info.plist
        info_plist_path = None
        for name in ipa.namelist():
            if name.endswith('Info.plist') and name.startswith('Payload/') and '.app/' in name:
                info_plist_path = name
                break

        if not info_plist_path:
            raise Exception("Info.plist not found in IPA")

        # Read plist
        with ipa.open(info_plist_path) as plist_file:
            plist_data = plistlib.load(plist_file)

        metadata = {
            "bundleIdentifier": plist_data.get("CFBundleIdentifier", ""),
            "bundleVersion": plist_data.get("CFBundleVersion", ""),
            "version": plist_data.get("CFBundleShortVersionString", ""),
            "name": plist_data.get("CFBundleDisplayName", plist_data.get("CFBundleName", "Unknown App")),
            "icon": None  # Optional: add icon path if desired
        }

        return metadata

def add_to_json_repo(metadata, ipa_url, json_repo_path):
    # Add download URL
    metadata["url"] = ipa_url

    # Load existing JSON or create a new list
    if os.path.isfile(json_repo_path):
        with open(json_repo_path, 'r') as f:
            try:
                repo = json.load(f)
            except json.JSONDecodeError:
                repo = []
    else:
        repo = []

    # Add or replace entry by bundleIdentifier
    repo = [entry for entry in repo if entry["bundleIdentifier"] != metadata["bundleIdentifier"]]
    repo.append(metadata)

    # Save updated JSON
    with open(json_repo_path, 'w') as f:
        json.dump(repo, f, indent=4)

    print(f"✅ Added {metadata['name']} to {json_repo_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_ipa_metadata.py <ipa_file_path> <ipa_download_url> <json_repo_path>")
        sys.exit(1)

    ipa_path = sys.argv[1]
    ipa_url = sys.argv[2]
    json_path = sys.argv[3]

    metadata = extract_metadata_from_ipa(ipa_path)
    add_to_json_repo(metadata, ipa_url, json_path)
