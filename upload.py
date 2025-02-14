import os
import json
import re
import paramiko
from scp import SCPClient

TGREEN = '\033[32m'
TRED = '\033[31m'
TRESET = '\033[0m'
TYELLOW = '\033[33m'

sourceforge_remote_path = "/home/frs/p/evolution-x"
sourceforge_host = "frs.sourceforge.net"
out = "../out/target/product/"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def upload_rom_file(device):
    rom_file = "../out/target/product/" + device + "/EvolutionX*.zip"
    if not os.path.exists(rom_file):
        print("ROM file not found. Exiting...")
        return
    else:
        print("ROM file found. Uploading...")
        os.system(f"rsync -avz --progress --partial --inplace --rsh=ssh {rom_file} {sourceforge_remote_path}")
        print("ROM file uploaded successfully.")

def upload_file(device, filename):
    pattern_rom = r'^Evolution.*\.zip$'
    with open(config_creds, "r") as f:
        data = json.load(f)
        username = data["username"]
        password = data["password"]
        android_version = data["android_version"]
    file_path = out + device + "/" + filename
    if re.match(pattern_rom, filename):
        try:
            if not os.path.exists(file_path):
                print(TRED + f"File {file_path} not found. Aborting...")
            else:
                remote_path = f"{sourceforge_remote_path}/{device}/{android_version}/"
                ssh.connect(hostname=sourceforge_host, username=username, password=password)
                scp = SCPClient(ssh.get_transport())
                print(TYELLOW + f"Sending {file_path} to {remote_path}... Please wait...")
                scp.put(file_path, f"{remote_path}")
                scp.close()
                print(TGREEN + f"Upload successful ! file available at https://sourceforge.net/projects/evolution-x/files/{device}/{android_version}/")

        except Exception as e:
            print(TRED + f"Failed to upload {file_path}: {str(e)}")
    else:
        filename_without_ext = os.path.splitext(filename)[0]
        try:
            if not os.path.exists(file_path):
                print(TRED + f"File {file_path} not found. Aborting...")
            else:
                remote_path = f"{sourceforge_remote_path}/{device}/{android_version}/{filename_without_ext}/"
                ssh.connect(hostname=sourceforge_host, username=username, password=password)
                scp = SCPClient(ssh.get_transport())
                print(TYELLOW + f"Sending {file_path} to {remote_path}... Please wait...")
                scp.put(file_path, f"{remote_path}")
                scp.close()
                print(TGREEN + f"Upload successful ! file available at https://sourceforge.net/projects/evolution-x/files/{device}/{android_version}/{filename_without_ext}/")

        except Exception as e:
            print(TRED + f"Failed to upload {file_path}: {str(e)}")


def retrieve_rom_name(device):
    pattern_rom = r'^Evolution.*\.zip$'
    if not os.path.exists(f"../out/target/product/{device}"):
        print(TRED + f"Device {device} not found. Aborting...")
    else:
        for dir in os.listdir(f"../out/target/product/{device}"):
            if re.match(pattern_rom, dir):
                return dir
    return None