#!/usr/bin/python3.6

import argparse
import logging
import logging.config
import re
import urllib.request

from xml.etree import ElementTree
from xml.dom import minidom

import untangle


logging.config.fileConfig(fname='log.cfg')
log = logging.getLogger('upload_zot_items')


def parse_jira_item(item_xml):
    """Extract Zotero attributes from a Jira item."""
    untangle_obj = untangle.parse(item_xml)

    key = untangle_obj.item.key.cdata

    # Save item to file.
    f = open("{0}.xml".format(key), "w")
    f.write(item_xml)
    f.close()

    log.debug('Title           : ' + untangle_obj.item.title.cdata)
    log.debug('Link            : ' + untangle_obj.item.link.cdata)
    log.debug('Key             : ' + key)
    log.debug('Type            : ' + untangle_obj.item.type.cdata)
    log.debug('Component       : ' + untangle_obj.item.component.cdata)

    # Affected Clients
    for customfield in untangle_obj.item.customfields.customfield:
        if customfield.customfieldname.cdata == 'Affected Clients':
            affected_clients = []
            for label in customfield.customfieldvalues.label:
                affected_clients.append(label.cdata)
            log.debug('Affected Clients: {0}'.format(affected_clients))

    # RPM Upgrade List
    for customfield in untangle_obj.item.customfields.customfield:
        if customfield.customfieldname.cdata == 'RPM Upgrade List':
            rpm_upgrade_list = []
            for customfieldvalue in customfield.customfieldvalues.customfieldvalue:
                rpm_upgrade_list.append(customfieldvalue.cdata)
            log.debug('RPM Upgrade List: {0}'.format(rpm_upgrade_list))

    # Changesets
    log.debug('List of Patches:')
    regex = re.compile(r'.*(https://forge.intelerad.com/hg[^\s"]+)"[\s]+[^\s>]+>([^\s>]+)<[^\s]+[\s]+[^\s]+[\s]+([^\s]+)')
    for comment in untangle_obj.item.comments.comment:
        if regex.search(comment.cdata):
            for match in regex.finditer(comment.cdata):
                patch_url = match.group(1).replace("rev", "raw-rev")
                patch_file = "{0}_{1}.patch".format(match.group(2).replace(":", "_"), match.group(3))
                log.debug("    Patch URL (File): {0} ({1})".format(patch_url, patch_file))
                # f = open(patch_file, "w")
                # f.write(urllib.request.urlopen(patch_url).read().decode('utf-8'))
                # f.close()

    log.debug('Session (end)   %s' % ('-' * 80))


def parse_jira_xml(args):
    """Extract Jira items from XML file."""
    with open(args.xml_filepath, 'r') as f:
        tree = ElementTree.parse(f)

    for item in tree.iter('item'):
        item_raw = ElementTree.tostring(item)
        item_doc = minidom.parseString(item_raw)
        item_xml = item_doc.toxml()
        parse_jira_item(item_xml)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Upload Jira tickets from XML file to Zotero Web API.')
    parser.add_argument(
        'xml_filepath',
        help='filepath of XML file that contains Jira tickets')
    return parser.parse_args()


def main():
    args = parse_arguments()
    parse_jira_xml(args)


if __name__ == "__main__":
    main()
