# Slack Export CSV Converter

## Overview

A simple tool that converts files exported from slack into CSV files.  
As a bonus attachment files are downloded as well.  
**This script only covers exports from Free/Pro plan; anything beyond that scope such as DMs would probably not get converted properly.**

## Prerequisites

- Python >=3.8
- Download/extract slack export to your computer
- Download/clone this repository to your computer

There are no external python dependencies for this script.

## Usage

Open the terminal and run the command below.  
Make sure to replace the paths appropriately.

```bash
python3 /location/of/script/slack_export_csv_converter/main.py /location/of/export
```

This will create a folder in the cwd of your terminal.  
All the converted CSV files of the exported messages, and additionally the attachment files of the messages (if any), will be stored in this folder.  
The exported files will remain intact.

Optionally you may pass a seceond argument to the script to explicitly designate where to newly create the folder at, instead of the default cwd.

```bash
python3 /location/of/script/slack_export_csv_converter/main.py /location/of/export /location/to/create/folder
```

## Structure of created folder

```
csv_converted_XXXXXXX/
├── channel01/
│   ├── messages.csv
│   ├── attachments.csv
│   └── attachments/
│       ├── 20230101_some_spreadsheet.xlsx
│       ├── 20230101_some_screenshot.jpg
│       └── ...
├── channel02/
│   ├── messages.csv
│   ├── attachments.csv
│   └── attachments/
│       └── ...
├── channel03/
│   └── ...
└── ...
```
