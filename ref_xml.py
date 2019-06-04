#!/usr/bin/python3.6

import argparse
import logging
import re
import untangle
import urllib.request
import xmltodict


logging.basicConfig(
    filename='ref_xml.log',
    level=logging.DEBUG
)
log = logging.getLogger('ref_xml')
log.setLevel(logging.DEBUG)

log.debug('Session (start) %s' % ('-' * 80))

parser = argparse.ArgumentParser(
    description='Upload Jira tickets from XML file to Zotero web application.')
parser.add_argument(
    'xml_filepath',
    help='filepath of XML file that contains Jira tickets')

args = parser.parse_args()

unt_obj = untangle.parse(args.xml_filepath)

key = unt_obj.rss.channel.item.key.cdata

with open(args.xml_filepath) as fxml:
    f = open("{0}.xml".format(key), "w")
    f.write(fxml.read())
    f.close()

print('Title           : ' + unt_obj.rss.channel.item.title.cdata)
print('Link            : ' + unt_obj.rss.channel.item.link.cdata)
print('Key             : ' + key)
print('Type            : ' + unt_obj.rss.channel.item.type.cdata)
print('Component       : ' + unt_obj.rss.channel.item.component.cdata)

log.debug('Title           : ' + unt_obj.rss.channel.item.title.cdata)
log.debug('Link            : ' + unt_obj.rss.channel.item.link.cdata)
log.debug('Key             : ' + key)
log.debug('Type            : ' + unt_obj.rss.channel.item.type.cdata)
log.debug('Component       : ' + unt_obj.rss.channel.item.component.cdata)

# Affected Clients
for customfield in unt_obj.rss.channel.item.customfields.customfield:
    if customfield.customfieldname.cdata == 'Affected Clients':
        affected_clients = []
        for label in customfield.customfieldvalues.label:
            affected_clients.append(label.cdata)
        print('Affected Clients: {0}'.format(affected_clients))
        log.debug('Affected Clients: {0}'.format(affected_clients))

# RPM Upgrade List
for customfield in unt_obj.rss.channel.item.customfields.customfield:
    if customfield.customfieldname.cdata == 'RPM Upgrade List':
        rpm_upgrade_list = []
        for customfieldvalue in customfield.customfieldvalues.customfieldvalue:
            rpm_upgrade_list.append(customfieldvalue.cdata)
        print('RPM Upgrade List: {0}'.format(rpm_upgrade_list))
        log.debug('RPM Upgrade List: {0}'.format(rpm_upgrade_list))

# Changesets
print('Comments:')
log.debug('Comments:')
regex = re.compile(r'.*(https://forge.intelerad.com/hg[^\s"]+)"[\s]+[^\s>]+>([^\s>]+)<[^\s]+[\s]+[^\s]+[\s]+([^\s]+)')
for comment in unt_obj.rss.channel.item.comments.comment:
    if regex.search(comment.cdata):
        print('    Comment (start)')
        log.debug('    Comment (start)')
        for match in regex.finditer(comment.cdata):
            patch_url = match.group(1).replace("rev", "raw-rev")
            patch_file = "{0}_{1}.patch".format(match.group(2).replace(":", "_"), match.group(3))
            print("        Patch URL (File): {0} ({1})".format(patch_url, patch_file))
            log.debug("        Patch URL (File): {0} ({1})".format(patch_url, patch_file))
            # f = open(patch_file, "w")
            # f.write(urllib.request.urlopen(patch_url).read().decode('utf-8'))
            # f.close()
        print('    Comment (end)')
        log.debug('    Comment (end)')
    else:
        print('    Comment (no patch)')
        log.debug('    Comment (no patch)')

log.debug('Session (end) %s' % ('-' * 80))
