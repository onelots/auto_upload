#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2025 The Evolution X Project
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import hashlib
import json
import datetime
import re
import configparser
from upload import get_android_ver

devices_conf = os.path.expanduser("~/auto_upload/devices.conf")
config = configparser.ConfigParser()
config.read(devices_conf)
devices = config.sections()
pwd = os.getenv("PWD")
out = os.getenv("ANDROID_PRODUCT_OUT")
top = os.getenv("ANDROID_BUILD_TOP")
rom_folder = top.split("/")[-1] if top else ""


def get_rom():
    if "lineage" in rom_folder:
        return "lineageos"
    elif "evo" in rom_folder.lower():
        return "evolution-x"


def get_timestamp_from_buildprop(buildprop_path):
    with open(buildprop_path, 'r') as f:
        for line in f:
            if "ro.system.build.date.utc" in line:
                return int(line.split('=')[1].strip())
    return 0


def get_checksum(file_path, checksum_type='md5'):
    if checksum_type == 'md5':
        return calculate_md5(file_path)
    elif checksum_type == 'sha256':
        return calculate_sha256(file_path)


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def generate_json(target_device):
    oem = config[target_device]["oem"]
    install_images = config[target_device]["install_images"]
    install_images = [img.strip() for img in install_images.split(",")]

    product_out = out
    output = os.path.join(product_out, f"{target_device}.json")

    zips = [f for f in os.listdir(product_out) if f.endswith(".zip") and "ota" not in f]
    if not zips:
        print(f"Error: no zip found in {product_out}")
        sys.exit(1)

    filename = max(zips, key=lambda f: re.search(r'\d{8}', f).group())
    build_date = re.search(r'\d{8}', filename).group()
    version = re.findall(r'\d+\.\d+', filename)[-1]

    rom = get_rom()
    android_version = get_android_ver()
    download_link = (
        "https://downloads.onelots.org/buckets/"
        f"onelots-builds-bucket/{rom}/{target_device}/{version}/{android_version}/{build_date}/{filename}"
    )

    maintainer = "Onelots"
    currently_maintained = False
    github = ""
    extra_images = []

    if os.path.exists(output):
        with open(output, 'r') as f:
            ota_data = json.load(f)
        response_data = ota_data["response"][0]
        maintainer = response_data.get("maintainer", maintainer)
        currently_maintained = response_data.get("currently_maintained", currently_maintained)
        github = response_data.get("github", github)
        extra_images = response_data.get("extra_images", extra_images)

    file_path = os.path.join(product_out, filename)
    buildprop = os.path.join(product_out, "system", "build.prop")
    timestamp = get_timestamp_from_buildprop(buildprop) or int(datetime.datetime.now().timestamp())

    md5 = get_checksum(file_path, 'md5')
    sha256 = get_checksum(file_path, 'sha256')
    size = os.path.getsize(file_path)

    json_data = {
        "response": [
            {
                "maintainer": maintainer,
                "currently_maintained": currently_maintained,
                "oem": oem,
                "device": target_device,
                "filename": filename,
                "download": download_link,
                "timestamp": timestamp,
                "md5": md5,
                "sha256": sha256,
                "size": size,
                "version": version,
                "buildtype": "userdebug",
                "forum": "https://discord.onelots.org",
                "firmware": "",
                "paypal": "https://paypal.me/0nel0ts",
                "github": github or "https://github.com/Onelots",
                "initial_installation_images": install_images,
                "extra_images": extra_images
            }
        ]
    }

    with open(output, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"{target_device}.json correctly generated.")


def main():
    if len(sys.argv) < 2:
        print("Usage: ./create_json.py <device>")
        sys.exit(1)

    target_device = sys.argv[1]

    if target_device not in devices:
        print(f"Error: '{target_device}' not found in {devices_conf}")
        print(f"Available devices: {', '.join(devices)}")
        sys.exit(1)

    generate_json(target_device)


if __name__ == "__main__":
    main()