#!/usr/bin/python3.6

import argparse
import untangle


parser = argparse.ArgumentParser(
    description='Upload Jira tickets from XML file to Zotero web application.')
parser.add_argument(
    'xml_filepath',
    metavar='xml_filepath',
    help='filepath of XML file that contains Jira tickets')

args = parser.parse_args()

obj = untangle.parse(args.xml_filepath)
print("title           : " + obj.rss.channel.item.title.cdata)
print("type            : " + obj.rss.channel.item.type.cdata)
print("component       : " + obj.rss.channel.item.component.cdata)

for customfield in obj.rss.channel.item.customfields.customfield:
    if customfield.customfieldname.cdata == "Affected Clients":
        print("affected clients:")
        for label in customfield.customfieldvalues.label:
            print("    " + label.cdata)

for customfield in obj.rss.channel.item.customfields.customfield:
    if customfield.customfieldname.cdata == "RPM Upgrade List":
        print("rpm upgrade list:")
        for customfieldvalue in customfield.customfieldvalues.customfieldvalue:
            print("    " + customfieldvalue.cdata)
