#!/usr/bin/env python3

import os
import sys
import configparser

rclone_conf = os.path.expanduser("~/.config/rclone/rclone.conf")
devices_conf = "devices.conf"

def check_conf():
    if not os.path.exists(rclone_conf):
        print("Rclone conf file not found, exiting...")
        sys.exit(1)
    print("Rclone configuration found, proceed.")

    if not os.path.exists(devices_conf):
        print("Device conf file not found, exiting...")
        sys.exit(1)
    print("Device configuration found, proceed.")

def read_device_config_file(file_path, built):
    config = configparser.ConfigParser()
    config.read(file_path)
    devices = config.sections()
    if built in devices:
        upload_device()
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
