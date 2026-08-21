#!/usr/bin/env python3

import os
from pathlib import Path
import configparser
import sys
from upload import get_android_ver

top = os.getenv("ANDROID_BUILD_TOP")
rom_folder = top.split("/")[-1]
devices_conf = os.path.expanduser("~/auto_upload/devices.conf")
config = configparser.ConfigParser()
config.read(devices_conf)
devices = config.sections()
overlay = "updater_overlay"
pwd = os.getenv("PWD")

def touch(f):
    Path(f).parent.mkdir(parents=True, exist_ok=True)
    Path(f).touch(exist_ok=True)

def get_rom():
    if "lineage" in rom_folder:
        return "lineageos"
    elif "evo" in rom_folder.lower():
        return "evolution-x"

def write_updater_strings(filepath, server_url, changelog_url, device):
    content = f'''
<?xml version="1.0" encoding="utf-8"?>
<!--
Copyright (C) 2017-2024 The LineageOS Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">

    <!-- Updater backend urls -->
    <string name="updater_server_url" translatable="false">{server_url}</string>
    <string name="menu_changelog_url" translatable="false">{changelog_url}<xliff:g id="device_name">{device}</xliff:g>.txt</string>
</resources>
            '''
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def populate_overlay(device):
    bucket = get_rom()
    rom_ver = rom_folder.lower()
    oem = config[device]["oem"]
    changelog_url = "https://example.com"
    android_ver = get_android_ver()
    server_url = f"https://raw.githubusercontent.com/downloads.onelots.org/buckets/{bucket}/OTA_UPDATES/{android_ver}/{device}.json"
    device_tree = f"device/{oem}/{device}"
    full_path = (f"{device_tree}/overlay_updater/packages/apps/Updater/app/src/main/res/values/strings.xml")
    touch(full_path)
    write_updater_strings(full_path, server_url, changelog_url, device)


def populate_overlay_path(lineage_path):
    with open(lineage_path, "a", encoding="utf-8") as f:
        f.write(f"\nDEVICE_PACKAGE_OVERLAYS += $(COMMON_PATH)/overlay_updater")

def to_do():
    print("Needs to be written")

def main():
    if len(sys.argv) < 3:
        print("Usage: script.py <device>")
        sys.exit(1)

    device = sys.argv[1]

    if device not in devices:
        print(f"Error: '{device}' not found in {devices_conf}")
        print(f"Available devices: {', '.join(devices)}")
        sys.exit(1)

    oem = config[device]["oem"]
    if sys.argv[2] == "add":
        populate_overlay(device)
        populate_overlay_path(f"device/{oem}/{device}/lineage_{device}.mk")
    elif sys.argv[2] == "remove":
        to_do()
main()
