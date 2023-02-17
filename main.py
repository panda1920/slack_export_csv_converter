# -*- coding: utf-8 -*-
from slack_export_csv_converter.logger import setup_logger


def return_hello():
    return "hello"


def main():
    setup_logger()


if __name__ == "__main__":
    main()

# expect a path
# use the path to discover channels folder and its files
# for each channel, load all the files
#   concatenate the files
#   perform data conversion
#   output to csv

# what components should there be
# component that deals with directory structure
# component that reads/writes file
# component that deals with message data conversion
# component that deals with attachment data generation/conversion?
# logger
