import requests
import os
import sys
import tempfile
import zipfile
import shutil
import subprocess
import tarfile
from logic.logging_config import log_call

LATEST_VERSION_URL = "https://raw.githubusercontent.com/Devaste/A2P_Cli/main/VERSION"
RELEASES_URL = "https://github.com/Devaste/A2P_Cli/releases/latest"

@log_call
def resource_path(relative_path):
    # Handles PyInstaller's _MEIPASS for bundled data files
    # PyInstaller sets _MEIPASS for bundled data files. Access is required and documented by PyInstaller (safe to ignore protected member warning).
    if hasattr(sys, '_MEIPASS'):  # noqa: SLF001
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', relative_path)

@log_call
def get_local_version():
    try:
        with open(resource_path('VERSION'), encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return None

@log_call
def get_latest_version():
    try:
        resp = requests.get(LATEST_VERSION_URL, timeout=5)
        if resp.ok:
            return resp.text.strip()
    except Exception:
        pass
    return None

@log_call
def get_relaunch_cmd():
    """
    Detects how the app was launched and returns the appropriate relaunch command as a list.
    Handles PyInstaller executables, Unix executables, and Python scripts.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller EXE (Windows or Unix)
        return [sys.executable]
    else:
        # Python script mode
        return [sys.executable, os.path.abspath(sys.argv[0])]

@log_call
def get_latest_release_assets():
    """
    Fetches the latest release assets from the GitHub API.
    Returns a dict mapping asset names to their download URLs.
    """
    api_url = "https://api.github.com/repos/Devaste/A2P_Cli/releases/latest"
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {asset['name']: asset['browser_download_url'] for asset in data.get('assets', [])}
    except Exception as e:
        print(f"[Update] Failed to fetch release assets: {e}")
        return {}

@log_call
def select_update_asset(assets):
    """
    Selects the correct asset name and URL based on platform and app type.
    Returns (asset_name, asset_url, asset_type).
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            for name in assets:
                if name.lower().endswith('.exe'):
                    return name, assets[name], 'exe'
        else:
            for name in assets:
                if name == 'A2P_Cli':
                    return name, assets[name], 'bin'
    else:
        # Prefer tar.gz for Unix, zip for Windows
        if sys.platform == 'win32':
            for name in assets:
                if name.endswith('.zip'):
                    return name, assets[name], 'zip'
        else:
            for name in assets:
                if name.endswith('.tar.gz'):
                    return name, assets[name], 'tar.gz'
    return None, None, None

@log_call
def download_asset(asset_url, asset_path):
    try:
        resp = requests.get(asset_url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(asset_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[Update] Download failed: {e}")
        return False

@log_call
def extract_asset(asset_type, asset_path, extract_dir, asset_name):
    os.makedirs(extract_dir, exist_ok=True)
    if asset_type == 'zip':
        try:
            with zipfile.ZipFile(asset_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        except Exception as e:
            print(f"[Update] Extraction failed: {e}")
            return False
    elif asset_type == 'tar.gz':
        try:
            with tarfile.open(asset_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
            return True
        except Exception as e:
            print(f"[Update] Extraction failed: {e}")
            return False
    else:
        try:
            target_path = os.path.join(extract_dir, asset_name)
            if isinstance(asset_path, bytes):
                asset_path = os.fsdecode(asset_path)
            if isinstance(target_path, bytes):
                target_path = os.fsdecode(target_path)
            shutil.move(asset_path, target_path)
            return True
        except Exception as e:
            print(f"[Update] Move failed: {e}")
            return False

@log_call
def write_updater_script(updater_path):
    updater_code = '''import os, sys, shutil, time, subprocess

def find_new_root(new_dir):
    for d in os.listdir(new_dir):
        candidate = os.path.join(new_dir, d)
        if os.path.isdir(candidate):
            return candidate
    raise RuntimeError("No valid new root found")

def copy_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def copy_or_replace(src, dst):
    if os.path.isdir(src):
        copy_tree(src, dst)
    else:
        shutil.copy2(src, dst)

def update_from_archive(old_dir, new_dir):
    new_root = find_new_root(new_dir)
    for item in os.listdir(new_root):
        s = os.path.join(new_root, item)
        d = os.path.join(old_dir, item)
        copy_or_replace(s, d)

def update_binary(old_dir, new_dir, asset_name):
    target = os.path.join(old_dir, asset_name)
    src = os.path.join(new_dir, asset_name)
    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(src, target)

def main():
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    asset_type = sys.argv[3]
    asset_name = sys.argv[4]
    relaunch_cmd = sys.argv[5:]
    time.sleep(1)
    if asset_type in ('zip', 'tar.gz'):
        update_from_archive(old_dir, new_dir)
    else:
        update_binary(old_dir, new_dir, asset_name)
    subprocess.Popen(relaunch_cmd)

if __name__ == "__main__":
    main()
'''
    with open(updater_path, "w", encoding="utf-8") as f:
        f.write(updater_code)

@log_call
def launch_updater_and_exit(updater_path, old_dir, extract_dir, asset_type, asset_name, relaunch_cmd):
    subprocess.Popen([sys.executable, updater_path, old_dir, extract_dir, asset_type, asset_name] + relaunch_cmd)
    print("[Update] Updater launched. Exiting for update...")
    os._exit(0)

@log_call
def download_and_prepare_update():
    """
    Download the correct asset for update, extract/replace as needed, write updater, and launch updater.
    """
    assets = get_latest_release_assets()
    asset_name, asset_url, asset_type = select_update_asset(assets)
    if not asset_url:
        print("[Update] No suitable update asset found.")
        return False

    temp_dir = tempfile.mkdtemp(prefix="a2p_update_")
    asset_path = os.path.join(temp_dir, asset_name)
    extract_dir = os.path.join(temp_dir, "new_version")
    updater_path = os.path.join(temp_dir, "a2p_updater.py")
    old_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    relaunch_cmd = get_relaunch_cmd()

    if not download_asset(asset_url, asset_path):
        shutil.rmtree(temp_dir)
        return False
    if not extract_asset(asset_type, asset_path, extract_dir, asset_name):
        shutil.rmtree(temp_dir)
        return False
    write_updater_script(updater_path)
    launch_updater_and_exit(updater_path, old_dir, extract_dir, asset_type, asset_name, relaunch_cmd)
    return None

@log_call
def check_for_update():
    local_version = get_local_version()
    latest_version = get_latest_version()
    if not local_version or not latest_version:
        return  # Silently skip if cannot check
    if latest_version != local_version:
        print(f"\nUpdate available: {latest_version} (You have {local_version})")
        print(f"Visit {RELEASES_URL} to download the latest version.\n")
        download_and_prepare_update()
