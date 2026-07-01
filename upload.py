#!/usr/bin/env python3

import os
import sys
import configparser
import subprocess
import re
import time
import requests
from datetime import date as date_module, timedelta, datetime

pwd = os.getenv("PWD")
top = os.getenv("ANDROID_BUILD_TOP")
out = os.getenv("ANDROID_PRODUCT_OUT")
rclone_conf = os.path.expanduser("~/.config/rclone/rclone.conf")
devices_conf = os.path.expanduser("~/auto_upload/devices.conf")
config = configparser.ConfigParser()
base_out = "out/target/product/"

roms_informations = {
    "roms_colors": {
        "lineageos": "167C80",
        "evolution-x": "005ffe"
    },
    "roms_images": {
        "lineageos": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQzJ5AMneN4WX2M6Xg_gapy6oQjqrZuCexIl0WhCRzSmw&s=10",
        "evolution-x": "https://pbs.twimg.com/media/HDoKAuvbEAAuv1E.jpg"
    },
    "roms_capitalized": {
        "lineageos": "LineageOS",
        "evolution-x": "EvolutionX"
    }
}

def get_zip_size(path):
    size = os.path.getsize(path)
    if size >= 1_000_000_000:
        return f"{size / 1_000_000_000:.1f} GB"
    return f"{size / 1_000_000:.0f} MB"

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

def send_webhook(rom, version, upload_path, device, rom_zip):
    webhook_url = os.getenv("WEBHOOK_URL")
    download_url = "https://downloads.onelots.org/" + upload_path
    rom_capitalized = roms_informations["roms_capitalized"][rom]
    if "lineageos" in rom:
        version = "lineageos-" + version
    size = get_zip_size(rom_zip)
    today = date_module.today().strftime("%d/%m/%Y")
    zip_name = rom_zip.split("/")[-1]
    build_time = int(os.getenv("BUILD_TIME"))
    time_elapsed = str(timedelta(seconds=int(time.time()) - build_time))
    rom_image_url = roms_informations["roms_images"][rom]
    rom_color = int(roms_informations["roms_colors"][rom], 16)
    now_timestamp = datetime.utcnow().isoformat()

    json_success = {
        "embeds": [{
            "author": {
                "name": f"New build for - {device}",
                "url": "https://onelots.org/devices"
            },
            "title": "Build succeeded !",
            "url": download_url,
            "description": f"Device : `{device}`\nRom built : `{rom_capitalized}`\nVersion : `{version}`\nSize : `{size}`\nDate : `{today}`\nZip name : `{zip_name}`\nTime elapsed: `{time_elapsed}`",
            "image": {"url": rom_image_url},
            "color": rom_color,
            "footer": {
                "text": "Onelots build services",
                "icon_url": "https://slate.dan.onl/slate.png"
            },
            "timestamp": now_timestamp
        }]
    }

    response = requests.post(webhook_url, json=json_success)
    response.raise_for_status()

def upload_device(device):
    rom = config[device]["rom"]
    android_version = get_android_ver(device)
    zips = [f for f in os.listdir(out) if f.endswith(".zip") and "ota" not in f]
    rom_zip = max(zips, key=lambda f: re.search(r'\d{8}', f).group())
    major_version = re.findall(r'\d+\.\d+', rom_zip)[-1]
    build_date = re.search(r'\d{8}', rom_zip).group()
    upload_path=f"{rom}/{device}/{android_version}/{major_version}/{build_date}"
    install_images = config[device]["install_images"]
    install_images = [img.strip() for img in install_images.split(",")]

    install_images.append(rom_zip)

    for image in install_images:
        if not image.endswith(".zip"):
            image = f"{image}.img"
        subprocess.run(["rclone", "copy", f"{out}/{image}", f"cloudflare-onelots:{upload_path}", "-P"])
    zip_path = f"{out}/{rom_zip}"
    send_webhook(rom, major_version, upload_path, device, zip_path)

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
