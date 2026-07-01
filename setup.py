#!/usr/bin/env python3

import os

def export_to_bashrc():
    bashrc = os.path.expanduser("~/.bashrc")
    function = """
miam() {
    local start=$(date +%s)
    brunch "$1"
    local exit_code=$?
    local duration=$(( $(date +%s) - start ))

    if [ $exit_code -eq 0 ]; then
        BUILD_TIME=$duration ~/auto_upload/upload.py "$1"
    fi
}
"""
    with open(bashrc, "a") as f:
        f.write(function)
    print("miam() added to ~/.bashrc, run 'source ~/.bashrc' to apply.")
    print("Do not forget to run :")
    print("export WEBHOOK_URL=yourwebhookurl")

export_to_bashrc()
