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
    except OSError:
        return None

@log_call
def get_latest_version():
    headers = {'User-Agent': 'A2P_Cli-Updater'}
    try:
        resp = requests.get(LATEST_VERSION_URL, headers=headers, timeout=5)
        if resp.ok:
            return resp.text.strip()
    except requests.exceptions.RequestException:
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
    Adds 'A2P_Cli-py.zip' and 'A2P_Cli-py.tar.gz' if present.
    """
    api_url = "https://api.github.com/repos/Devaste/A2P_Cli/releases/latest"
    headers = {'User-Agent': 'A2P_Cli-Updater'}
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        assets = {asset['name']: asset['browser_download_url'] for asset in data.get('assets', [])}
        # Add GitHub auto-generated source code archives as fallback
        if 'zipball_url' in data:
            assets['Source code (zip)'] = data['zipball_url']
        if 'tarball_url' in data:
            assets['Source code (tar.gz)'] = data['tarball_url']
        return assets
    except Exception as e:
        print(f"[Update] Failed to fetch release assets: {e}")
        return {}

@log_call
def select_update_asset(assets):
    """
    Select the correct asset for update based on how the app was launched.
    Prefer patch archive if available, otherwise fallback to full archive.
    Returns (asset_name, asset_url, asset_type).
    - .exe if running from a2pcli.exe (Windows frozen)
    - a2pcli if running from a2pcli (Linux/Mac frozen)
    - patch.zip if running as .py on Windows and patch exists
    - patch.tar.gz if running as .py on Linux/Mac and patch exists
    - .zip if running as .py on Windows
    - .tar.gz if running as .py on Linux/Mac
    """
    exe_name = 'A2P_Cli.exe'
    bin_name = 'A2P_Cli'
    zip_name = 'A2P_Cli-py.zip'
    tar_name = 'A2P_Cli-py.tar.gz'
    patch_zip = 'A2P_Cli-patch.zip'
    patch_tar = 'A2P_Cli-patch.tar.gz'

    is_frozen = getattr(sys, 'frozen', False)
    is_win = sys.platform == 'win32'

    if is_frozen:
        # Running as frozen executable
        if is_win:
            if exe_name in assets:
                return exe_name, assets[exe_name], 'exe'
        else:
            if bin_name in assets:
                return bin_name, assets[bin_name], 'bin'
    else:
        # Running as Python script
        if is_win:
            if patch_zip in assets:
                return patch_zip, assets[patch_zip], 'zip'
            elif zip_name in assets:
                return zip_name, assets[zip_name], 'zip'
        else:
            if patch_tar in assets:
                return patch_tar, assets[patch_tar], 'tar.gz'
            elif tar_name in assets:
                return tar_name, assets[tar_name], 'tar.gz'
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
import traceback

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

MAX_RETRIES = 10
RETRY_DELAY = 1  # seconds

# LOGFILE will be set in main() based on old_dir
LOGFILE = None

def log(msg):
    global LOGFILE
    with open(LOGFILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\\n')

def list_dir(path):
    for root, dirs, files in os.walk(path):
        for name in dirs:
            log(f"[DIR] {os.path.join(root, name)}")
        for name in files:
            log(f"[FILE] {os.path.join(root, name)}")

def copy_all_recursive(src, dst):
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_root = os.path.join(dst, rel_path) if rel_path != '.' else dst
        if not os.path.exists(target_root):
            os.makedirs(target_root, exist_ok=True)
        for d in dirs:
            dir_path = os.path.join(target_root, d)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_root, f)
            for retry in range(MAX_RETRIES):
                try:
                    log(f"[Updater] Copying file: {src_file} -> {dst_file}")
                    shutil.copy2(src_file, dst_file)
                    break
                except Exception as e:
                    log(f"[Updater] Retry {retry+1}/{MAX_RETRIES} failed to copy {src_file} to {dst_file}: {e}")
                    time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"[Updater] Failed to copy {src_file} to {dst_file} after {MAX_RETRIES} retries")

def find_new_root(new_dir):
    for d in os.listdir(new_dir):
        candidate = os.path.join(new_dir, d)
        if os.path.isdir(candidate):
            if any(os.path.exists(os.path.join(candidate, fname)) for fname in ("main.py", "VERSION")):
                return candidate
    for d in os.listdir(new_dir):
        candidate = os.path.join(new_dir, d)
        if os.path.isdir(candidate):
            return candidate
    raise RuntimeError("No valid new root found")

def update_from_archive(old_dir, new_dir):
    new_root = find_new_root(new_dir)
    log(f"[Updater] new_root={new_root}, old_dir={old_dir}")
    list_dir(new_root)
    list_dir(old_dir)
    copy_all_recursive(new_root, old_dir)
    list_dir(old_dir)

def update_binary(old_dir, new_dir, asset_name):
    log(f"[Updater] update_binary: {old_dir} <- {new_dir}")
    list_dir(new_dir)
    list_dir(old_dir)
    copy_all_recursive(new_dir, old_dir)
    list_dir(old_dir)

def relaunch_app(cmd):
    if len(cmd) >= 2 and cmd[0].lower().endswith('python.exe'):
        relaunch = ['python', cmd[1]]
    else:
        relaunch = cmd
    log(f"[Updater] Relaunching: {' '.join(relaunch)}")
    if sys.platform == "win32":
        try:
            # Build the relaunch command as a single string for 'start'
            cmd_str = ' '.join(relaunch)
            subprocess.Popen(f'start "" {cmd_str}', shell=True)
        except Exception:
            subprocess.Popen(relaunch, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True)
    else:
        subprocess.Popen(relaunch, preexec_fn=os.setsid, close_fds=True)
    os._exit(0)

def main():
    global LOGFILE
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    asset_type = sys.argv[3]
    asset_name = sys.argv[4]
    relaunch_cmd = sys.argv[5:]
    no_relaunch = False
    if '--no-relaunch' in relaunch_cmd:
        no_relaunch = True
        relaunch_cmd.remove('--no-relaunch')
    LOGFILE = os.path.join(old_dir, 'update.log')
    try:
        if asset_type in ('zip', 'tar.gz'):
            update_from_archive(old_dir, new_dir)
        else:
            update_binary(old_dir, new_dir, asset_name)
        log("[Update] Update complete!")
        if not no_relaunch:
            log("[Update] Relaunching app...")
            relaunch_app(relaunch_cmd)
        else:
            log("[Update] Relaunch skipped (CLI mode).")
    except Exception as e:
        log(f"[Update] Update failed: {e}\\n{traceback.format_exc()}")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
'''
    with open(updater_path, "w", encoding="utf-8") as f:
        f.write(updater_code)

@log_call
def launch_updater_and_exit(updater_path, old_dir, extract_dir, asset_type, asset_name, relaunch_cmd, no_relaunch=False):
    args = [sys.executable, updater_path, old_dir, extract_dir, asset_type, asset_name] + relaunch_cmd
    if no_relaunch:
        args.append('--no-relaunch')
    subprocess.Popen(args)
    os._exit(0)

@log_call
def download_and_prepare_update(asset_url=None, asset_name=None, asset_type=None, no_relaunch=False):
    """
    Download the specified asset for update, extract/replace as needed, write updater, and launch updater.
    If asset_url, asset_name, asset_type are not provided, fetch and select automatically (CLI fallback).
    """
    if asset_url is None or asset_name is None or asset_type is None:
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
        cleanup_and_report(temp_dir, "[Update] Download failed.")
        return False
    if not extract_asset(asset_type, asset_path, extract_dir, asset_name):
        cleanup_and_report(temp_dir, "[Update] Extraction failed.")
        return False
    write_updater_script(updater_path)
    launch_updater_and_exit(updater_path, old_dir, extract_dir, asset_type, asset_name, relaunch_cmd, no_relaunch=no_relaunch)
    return None

@log_call
def cleanup_and_report(temp_dir, msg):
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass
    print(msg)

@log_call
def check_for_update():
    local = get_local_version()
    latest = get_latest_version()
    if not latest or not local:
        print("[Update] Could not determine version information.")
    elif latest == local:
        print(f"[Update] You are running the latest version: {local}.")
    else:
        print(f"Update available: {latest} (You have {local})")
        answer = input("Update now? [Y/n]: ").strip().lower()
        if answer in ("", "y", "yes"):
            try:
                download_and_prepare_update(no_relaunch=True)
            except Exception as e:
                print(f"[Update] Error: {e}")
