# -*- coding: utf-8 -*-
print("Hello world!")


def return_hello():
    return "hello"


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
