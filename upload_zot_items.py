#!/usr/bin/python3.6

import argparse
import logging
import logging.config
import re
import urllib.request

from xml.etree import ElementTree
from xml.dom import minidom

import untangle

from upload_zot_items_utils import sort_pacs_versions
from upload_zot_items_utils import transform


logging.config.fileConfig(fname='log.cfg')
log = logging.getLogger('upload_zot_items')


def parse_jira_item(item_xml, args):
    """Extract Zotero attributes from one Jira item."""
    untangle_obj = untangle.parse(item_xml)

    key = untangle_obj.item.key.cdata

    # Save item to file.
    f = open("{0}.xml".format(key), "w")
    f.write(item_xml)
    f.close()

    log.debug('Item (start) %s' % ('-' * 80))
    log.debug('Title           : ' + untangle_obj.item.title.cdata)
    log.debug('Link            : ' + untangle_obj.item.link.cdata)
    log.debug('Key             : ' + key)
    log.debug('Type            : ' + untangle_obj.item.type.cdata)
    log.debug('Component       : ' + untangle_obj.item.component.cdata)

    # Collect tags as Jira item is processed.
    tags = args.common_tags[:] # Copy list contents

    # Affected Clients
    affected_clients = []
    for customfield in untangle_obj.item.customfields.customfield:
        if customfield.customfieldname.cdata == 'Affected Clients':
            for label in customfield.customfieldvalues.label:
                affected_client = 'client_' + label.cdata.lower()
                affected_clients.append(affected_client)
                if affected_client not in tags:
                    tags.append(affected_client)
    if not any(element.startswith('client_') for element in tags):
        tags.append('client_none')
    log.debug('Affected Clients: {0}'.format(affected_clients))

    # RPM Upgrade List
    rpm_upgrade_list = []
    for customfield in untangle_obj.item.customfields.customfield:
        if customfield.customfieldname.cdata == 'RPM Upgrade List':
            for customfieldvalue in customfield.customfieldvalues.customfieldvalue:
                rpm = 'rpm_' + customfieldvalue.cdata
                rpm_upgrade_list.append(rpm)
                if rpm not in tags:
                    tags.append(rpm)
    log.debug('RPM Upgrade List: {0}'.format(rpm_upgrade_list))

    # Changesets
    log.debug('List of Patches:')
    regex = re.compile(r'.*(https://forge.intelerad.com/hg[^\s"]+)"[\s]+[^\s>]+>([^\s>]+)<[^\s]+[\s]+[^\s]+[\s]+([^\s]+)')
    pacs_versions = []
    for comment in untangle_obj.item.comments.comment:
        if regex.search(comment.cdata):
            # Save raw patch to file.
            for match in regex.finditer(comment.cdata):
                patch_url = match.group(1).replace("rev", "raw-rev")
                component_version = match.group(3)
                patch_file = "{0}_{1}.patch".format(match.group(2).replace(":", "_"), component_version)
                if component_version.startswith('PACS') and component_version not in pacs_versions:
                    pacs_versions.append(component_version)
                log.debug("    Patch URL (File): {0} ({1})".format(patch_url, patch_file))
                # f = open(patch_file, "w")
                # f.write(urllib.request.urlopen(patch_url).read().decode('utf-8'))
                # f.close()
            # Add earliest PACS version where patch was applied.
    if pacs_versions:
        pacs_versions = sort_pacs_versions(pacs_versions)
        formatted_pacs_version = pacs_versions[0].lower()
        if formatted_pacs_version not in tags:
            tags.append('fixed_' + formatted_pacs_version)

    tags.sort()
    log.debug('PACS Versions   : {0}'.format(pacs_versions))
    log.debug('Tags            : {0}'.format(tags))
    log.debug('Item (end)   %s' % ('-' * 80))


def parse_jira_xml(args):
    """Extract Jira items from XML file."""
    with open(args.xml_filepath, 'r') as f:
        tree = ElementTree.parse(f)

    for item in tree.iter('item'):
        item_raw = ElementTree.tostring(item)
        item_doc = minidom.parseString(item_raw)
        item_xml = item_doc.toxml()
        parse_jira_item(item_xml, args)


def parse_arguments():
    """Extract arguments and options from command line."""
    parser = argparse.ArgumentParser(
        description='Upload Jira tickets from XML file to Zotero Web API.')
    parser.add_argument(
        'xml_filepath',
        help='filepath of XML file that contains Jira tickets')
    parser.add_argument(
        '--tag', action='append',
        dest='common_tags',
        default=['ticket_jira'],
        help='command tags to assign to all uploaded items')
    args = parser.parse_args()
    log.debug('Arguments Passed (start) %s' % ('-' * 68))
    log.debug('xml_filepath: {0}'.format(args.xml_filepath))
    log.debug('common_tags : {0}'.format(args.common_tags))
    log.debug('Arguments Passed (end)   %s' % ('-' * 68))
    return args


def main():
    args = parse_arguments()
    parse_jira_xml(args)


if __name__ == "__main__":
    main()
