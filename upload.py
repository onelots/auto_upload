#!/usr/bin/env python3

import os
import sys
import configparser
import subprocess
import re

pwd = os.getenv("PWD")
top = os.getenv("ANDROID_BUILD_TOP")
out = os.getenv("ANDROID_PRODUCT_OUT")
rclone_conf = os.path.expanduser("~/.config/rclone/rclone.conf")
devices_conf = os.path.expanduser("~/auto_upload/devices.conf")
config = configparser.ConfigParser()
base_out = "out/target/product/"


def check_conf():
    if not os.path.exists(rclone_conf):
        print("Rclone conf file not found, exiting...")
        sys.exit(1)
    print("Rclone configuration found, proceed.")

    if not os.path.exists(devices_conf):
        print("Device conf file not found, exiting...")
        sys.exit(1)
    print("Device configuration found, proceed.")


def get_android_ver(device):
    rom = config[device]["rom"]
    if "lineage" in rom:
        if "lineage-18" in pwd:
            aver = 11
        if "lineage-19" in pwd:
            aver = 12
        if "lineage-20" in pwd:
            aver = 13
        if "lineage-21" in pwd:
            aver = 14
        if "lineage-22" in pwd:
            aver = 15
        if "lineage-23" in pwd:
            aver = 16
        if "lineage-24" in pwd:
            aver = 17
    if "evolutionx" in rom:
        if "10" in pwd:
            aver = 15
        if "11" in pwd:
            aver = 16
        if "12" in pwd:
            aver = 17
    
    return int(aver)


def upload_device(device):
    rom = config[device]["rom"]
    android_version = get_android_ver(device)
    zips = [f for f in os.listdir(out) if f.endswith(".zip") and "ota-eng" not in f]
    rom_zip = max(zips, key=lambda f: re.search(r'\d{8}', f).group())
    major_version = re.findall(r'\d+\.\d+', rom_zip)[-1]
    build_date = re.search(r'\d{8}', rom_zip).group()
    upload_path=f"{rom}/{device}/{android_version}/{major_version}/{build_date}"
    install_images = config[device]["install_images"]
    install_images = [img.strip() for img in install_images.split(",")]
    
    install_images.append(rom_zip)

    # Upload stuff
    for image in install_images:
        if not image.endswith(".zip"):
            image = f"{image}.img"
        subprocess.run(["rclone", "copy", f"{out}/{image}", f"cloudflare-onelots:{upload_path}", "-P"])


def read_device_config_file(file_path, built):
    config.read(file_path)
    devices = config.sections()
    if built in devices:
        upload_device(built)
    else:
        print(f"Device '{built}' not found in config, exiting...")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./upload.py <device>")
        sys.exit(1)
    built = sys.argv[1]
    check_conf()
    read_device_config_file(devices_conf, built)

main()
