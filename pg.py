#!/usr/local/bin/python3

import argparse

parser = argparse.ArgumentParser(
    description='Upload Jira tickets from XML file to Zotero web application.')
parser.add_argument(
    'xml-filepath',
    metavar='xml-filepath',
    help='filepath of XML file that contains Jira tickets')

args = parser.parse_args()
