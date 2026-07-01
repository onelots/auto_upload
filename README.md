<div align='center'>

<h1>Auto Uploader</h1>
<p>Automatically upload LineageOS/EvolutionX builds to S3 after compilation.</p>

<h4> <span> · </span> <a href="https://github.com/Oneloutre/auto_upload/blob/master/README.md"> Documentation </a> <span> · </span> <a href="https://github.com/Oneloutre/auto_upload/issues"> Report Bug </a> <span> · </span> <a href="https://github.com/Oneloutre/auto_upload/issues"> Request Feature </a> </h4>

![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=flat) ![Android Badge](https://img.shields.io/badge/Android-3DDC84?logo=android&logoColor=fff&style=flat) ![Linux Badge](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=fff&style=flat) ![License Badge](https://img.shields.io/badge/License-MIT-000000?style=flat)

</div>

## What is it ?

I maintain several devices. When releasing a new build, uploading files manually for each device is tedious. This script hooks into the build system and uploads everything automatically once the build succeeds.

## Roadmap

| Feature                        | Done ? |
| :------------------------------:| :------:|
| Device config file             | ✅      |
| LineageOS & EvolutionX support | ✅      |
| S3 upload via rclone           | ✅      |
| Custom mirrors support         | ❌      |

## Installation

Clone the repo at the root of your Android build tree, then install dependencies and run the setup :

```bash
croot
git clone https://github.com/Oneloutre/auto_upload.git
cd auto_upload
pip3 install -r requirements.txt
./setup.py
source ~/.bashrc
```

`setup.py` adds a `miam()` function to your `~/.bashrc`. This function wraps `brunch`, detects if the build succeeded, and calls `upload.py` automatically.

## Configuration

Edit `devices.conf` to declare your devices :

```ini
[ibiza]
rom=lineageos
install_images=dtbo, boot, vendor_boot

[hotdogb]
rom=evolutionx
install_images=vbmeta, dtbo, recovery
```

## Usage

Instead of `brunch <device>`, use :

```bash
miam <device>
```

If the build succeeds, the relevant images are uploaded to your S3 bucket via rclone. No further action needed.

## Contact

Discord : `onelots`

Mail : `onelots@onelots.fr`

GitHub : [https://github.com/Oneloutre/auto_upload](https://github.com/Oneloutre/auto_upload)
