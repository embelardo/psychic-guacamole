#!/usr/bin/python3.6

import argparse
import json
import pprint
import re
import untangle
import urllib.request
import xmltodict


parser = argparse.ArgumentParser(
    description='Upload Jira tickets from XML file to Zotero web application.')
parser.add_argument(
    'xml_filepath',
    help='filepath of XML file that contains Jira tickets')

args = parser.parse_args()

unt_obj = untangle.parse(args.xml_filepath)

key = unt_obj.rss.channel.item.key.cdata

pp = pprint.PrettyPrinter(indent=4)
with open(args.xml_filepath) as fxml:
    json = json.dumps(xmltodict.parse(fxml.read()))
    f = open("{0}.txt".format(key), "w")
    f.write(pp.pformat(json))
    f.close()

print('Title           : ' + unt_obj.rss.channel.item.title.cdata)
print('Link            : ' + unt_obj.rss.channel.item.link.cdata)
print('Key             : ' + key)
print('Type            : ' + unt_obj.rss.channel.item.type.cdata)
print('Component       : ' + unt_obj.rss.channel.item.component.cdata)

# Affected Clients
for customfield in unt_obj.rss.channel.item.customfields.customfield:
    if customfield.customfieldname.cdata == 'Affected Clients':
        print('Affected Clients:', end=' ')
        affected_clients = []
        for label in customfield.customfieldvalues.label:
            affected_clients.append(label.cdata)
        print(affected_clients)

# RPM Upgrade List
for customfield in unt_obj.rss.channel.item.customfields.customfield:
    if customfield.customfieldname.cdata == 'RPM Upgrade List':
        print('RPM Upgrade List:', end=' ')
        rpm_upgrade_list = []
        for customfieldvalue in customfield.customfieldvalues.customfieldvalue:
            rpm_upgrade_list.append(customfieldvalue.cdata)
        print(rpm_upgrade_list)

# Changesets
print('Comments with Patches:')
# regex = re.compile(r'.*(https://forge.intelerad.com/hg[^\s"]+)"[\s]+[^\s]+[\s]+[^\s]+[\s]+([^\s]+)')
# regex = re.compile(r'.*(https://forge.intelerad.com/hg[^\s"]+)"[\s]+[^\s>]+>([^\s>]+)<')
regex = re.compile(r'.*(https://forge.intelerad.com/hg[^\s"]+)"[\s]+[^\s>]+>([^\s>]+)<[^\s]+[\s]+[^\s]+[\s]+([^\s]+)')
for comment in unt_obj.rss.channel.item.comments.comment:
    for match in regex.finditer(comment.cdata):
        patch_url = match.group(1).replace("rev", "raw-rev")
        print("Patch URL: {0} ".format(patch_url))
        patch_file = "{0}_{1}.patch".format(match.group(2).replace(":", "_"), match.group(3))
        print("     File: {0}".format(patch_file))
        f = open(patch_file, "w")
        f.write(urllib.request.urlopen(patch_url).read().decode('utf-8'))
        f.close()
        f = open(patch_file, "r")
        # print(f.read())
        print('... ')
    print('----- ' * 10)
