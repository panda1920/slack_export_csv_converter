# Slack Export CSV Converter

Converts files exported from slack into CSV files.
As a bonus attachment files are downloded as well.
**This script only covers exports by Free/Pro plan; anything beyond that scope such as DMs would probably not get converted properly.**

## Prerequisites

- Python >3.8
- Download/extract slack export to your computer

## Usage

## Folder structure of converted files

```
csv_generated/
├── channel01/
│   ├── channel01.csv
│   ├── channel01_attachments.csv
│   └── attachments/
│       ├── 20230101_some_spreadsheet.xlsx
│       └── 20230101_some_screenshot.jpg
├── channel02/
│   ├── channel02.csv
│   ├── channel02_attachments.csv
│   └── attachments/
│       └── ...
└── channel03/
    └── ...
```
