#!/usr/bin/python3.6

import argparse
import configparser
import logging
import logging.config
import os
import re
import shutil
import time
import uuid

from contextlib import closing
from datetime import datetime
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.etree import ElementTree
from xml.dom import minidom

import hglib
import untangle

from upload_zot_items_utils import format_jira_date
from upload_zot_items_utils import sort_pacs_versions
from upload_zot_items_utils import transform

from upload_zot_items_web_api import TAG_TICKET_JIRA

from upload_zot_items_web_api import create_collection
from upload_zot_items_web_api import create_item
from upload_zot_items_web_api import item_exists
from upload_zot_items_web_api import upload_file_attachments

TARGET_COLLECTION = 'uploaded_jira_tickets'

config = configparser.ConfigParser()
config.read('upload_zot_items.cfg')

patch_url_prefix = config['upload_zot_items']['patch_url_prefix']
patch_server = config['upload_zot_items']['patch_server']
patch_test_server = config['upload_zot_items']['patch_test_server']
intelepacs_repo_path = config['upload_zot_items']['intelepacs_repo_path']
email_address = config['upload_zot_items']['email_address']

use_local_intelepacs_repo = os.path.exists(intelepacs_repo_path)
hg_client = None
if use_local_intelepacs_repo:
    hg_client = hglib.open(intelepacs_repo_path)

logging.config.fileConfig(fname='log.cfg')
log = logging.getLogger('log')


def remove_directory(dir_name):
    """Remove directory and all its contents."""
    shutil.rmtree(dir_name)


def create_directory(dir_name):
    """Create directory and fail if it already exists."""
    os.makedirs(dir_name)


def create_random_dir_name(key):
    """Create directory name using a uuid."""
    return 'tmp/{0}_{1}'.format(key, str(uuid.uuid1()))


def save_patch_from_remote_repo(patch_url, patch_filename, patch_filepath, committer, committer_regex):
    """Get patch contents from server and save to file."""
    try:
        log.debug('  {0} | {1}'.format(patch_url, patch_filename))
        with closing(urlopen(patch_url)) as response:  # response is auto-closed
            # Save patch to file
            patch_content_bytes = response.read()
            patch_content = patch_content_bytes.decode('ISO-8859-1')
            f = open(patch_filepath, 'w')
            f.write(patch_content)
            f.close()
            # Try to get committer
            if not committer:
                committer_match = committer_regex.search(patch_content)
                if committer_match:
                    committer = committer_match.group(1)
    except Exception as error:
        log.debug(error)
        log.debug('      Error accessing URL from remote repo [{0}]'.format(patch_url))


def save_patch_from_local_repo(rev, patch_filename, patch_filepath, committer, committer_regex):
    """Get patch contents from local repo and save to file."""
    try:
        log.debug('  {0} | {1}'.format(rev, patch_filename))
        # Save patch to file
        patch_content_bytes = hg_client.diff(revs=[], change=rev, showfunction=True, ignoreallspace=True, unified=5, subrepos=False)
        patch_content = patch_content_bytes.decode('ISO-8859-1')
        f = open(patch_filepath, 'w')
        f.write(patch_content)
        f.close()
        # Try to get committer
        if not committer:
            committer_match = committer_regex.search(patch_content)
            if committer_match:
                committer = committer_match.group(1)
    except Exception as error:
        log.debug(error)
        log.debug('      Error accessing revision from local repo [{0}]'.format(rev))


def save_patches_to_file(tags, untangle_obj, dir_name):
    """Save raw patch contents to a file.
       Extract earliest PACS version patched and convert into fixed version tag.
       Extract latest patch date and convert into circa tag.
    """
    log.debug('Patch List      :')
    patch_url_pattern = '.*(' + patch_url_prefix + '[^\s"]+)"[\s]+[^\s>]+>([^\s>]+)<[^\s]+[\s]+[^\s]+[\s]+([^\s]+)'
    patch_url_regex = re.compile(patch_url_pattern)
    jira_date = None
    pacs_versions = []
    committer_pattern = '.*<([a-z]+)(' + email_address + ').*'
    committer_regex = re.compile(committer_pattern)
    committer = None
    for comment in untangle_obj.item.comments.comment:
        if patch_url_regex.search(comment.cdata):
            jira_date = comment['created']
            # log.debug('Patch Commit Date: '.format(jira_date))
            # Save raw patch to file.
            for match in patch_url_regex.finditer(comment.cdata):
                patch_url = match.group(1).replace('rev', 'raw-rev')
                patch_url = patch_url.replace(patch_server, patch_test_server)
                component_version = match.group(3)
                repo_rev = match.group(2).split(':')
                repo = repo_rev[0]
                rev = repo_rev[1]
                patch_filename = '{0}_{1}_{2}.patch.txt'.format(repo, component_version, rev)
                patch_filepath = '{0}/{1}'.format(dir_name, patch_filename)
                if component_version not in pacs_versions:
                    pacs_versions.append(component_version)
                if repo == 'intelepacs' and use_local_intelepacs_repo:
                    patch_content = save_patch_from_local_repo(rev, patch_filename, patch_filepath, committer, committer_regex)
                else:
                    patch_content = save_patch_from_remote_repo(patch_url, patch_filename, patch_filepath, committer, committer_regex)
    # Add committer tag
    if committer:
        tags.append('committer_{0}'.format(committer.lower()))
    # Add latest patch commit date as circa tag
    circa_tag = 'fixed_circa_' + format_jira_date(jira_date) if jira_date else 'fixed_circa_no_date'
    # log.debug('Circa Tag: {0}'.format(circa_tag))
    tags.append(circa_tag)
    # Add earliest PACS version where patch was applied as a fixed version tag.
    if pacs_versions:
        pacs_versions = sort_pacs_versions(pacs_versions)
        formatted_pacs_version = pacs_versions[0].lower()
        if formatted_pacs_version not in tags:
            tags.append('fixed_' + formatted_pacs_version)
    # log.debug('PACS Versions   : {0}'.format(pacs_versions))


def add_affected_client_tags(tags, untangle_obj):
    """Extract affected clients and convert them into client tags."""
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


def add_rpm_tags(tags, untangle_obj):
    """Extract upgrade RPMs and convert them into rpm tags."""
    rpm_upgrade_list = []
    for customfield in untangle_obj.item.customfields.customfield:
        if customfield.customfieldname.cdata == 'RPM Upgrade List':
            for customfieldvalue in customfield.customfieldvalues.customfieldvalue:
                rpm = 'rpm_' + customfieldvalue.cdata
                rpm_upgrade_list.append(rpm)
                if rpm not in tags:
                    tags.append(rpm)
    log.debug('RPM Upgrade List: {0}'.format(rpm_upgrade_list))


def save_item_to_file(dir_name, key, item_xml):
    item_file = '{0}/{1}.xml'.format(dir_name, key)
    f = open(item_file, 'w')
    f.write(item_xml)
    f.close()


def parse_jira_item(args, item_xml, target_collection_id):
    """Extract Zotero attributes from one Jira item."""
    untangle_obj = untangle.parse(item_xml)

    title = untangle_obj.item.title.cdata
    if item_exists(title, TAG_TICKET_JIRA):
        log.debug('Item [{0}] already exists. Skipping.'.format(title))
        return False

    key = untangle_obj.item.key.cdata

    dir_name = create_random_dir_name(key)
    create_directory(dir_name)

    save_item_to_file(dir_name, key, item_xml)

    ticket_type = untangle_obj.item.type.cdata

    url = untangle_obj.item.link.cdata

    log.debug('Item (start) %s' % ('-' * 80))
    log.debug('Key             : ' + key)
    log.debug('Item Directory  : ' + dir_name)
    log.debug('Title           : ' + title)
    log.debug('Link            : ' + url)
    log.debug('Type            : ' + ticket_type)

    # Add tags as item is processed.
    tags = args.common_tags[:]

    # There can be multiple components
    try:
        component = untangle_obj.item.component
        if isinstance(component, list):
            log.debug('Component       : {0}'.format(untangle_obj.item.component))
            for element in component:
                tags.append(transform(element.cdata))
        else:
            log.debug('Component       : {0}'.format(component.cdata))
            tags.append(transform(component.cdata))
    except AttributeError:
        log.debug('Component       : None')

    tags.append('ticket_' + transform(ticket_type))

    add_affected_client_tags(tags, untangle_obj)

    add_rpm_tags(tags, untangle_obj)

    save_patches_to_file(tags, untangle_obj, dir_name)

    # Create item in Zotero Web API
    tags.sort()
    item_id = create_item(target_collection_id, key, title, url, tags)
    upload_status = upload_file_attachments(item_id, dir_name)
    log.debug('Upload Success  : {0}'.format(upload_status))
    remove_directory(dir_name)

    log.debug('Tags            : {0}'.format(tags))
    log.debug('Item (end)   %s' % ('-' * 80))
    return True


def parse_jira_xml(args, target_collection_id):
    """Extract Jira items from XML file."""
    with open(args.xml_filepath, 'r') as f:
        tree = ElementTree.parse(f)

    for item in tree.iter('item'):
        item_raw = ElementTree.tostring(item)
        item_doc = minidom.parseString(item_raw)
        item_xml = item_doc.toxml()
        item_created = parse_jira_item(args, item_xml, target_collection_id)
        # Pause between item creations like a good citizen
        if item_created:
            time.sleep(3)


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
        default=[TAG_TICKET_JIRA],
        help='command tags to assign to all uploaded items')
    args = parser.parse_args()
    log.debug('Arguments Passed (start) %s' % ('-' * 68))
    log.debug('xml_filepath: {0}'.format(args.xml_filepath))
    log.debug('common_tags : {0}'.format(args.common_tags))
    log.debug('Arguments Passed (end)   %s' % ('-' * 68))
    return args


def main():
    args = parse_arguments()
    target_collection_id = create_collection(TARGET_COLLECTION)
    if not target_collection_id:
        log.debug('Target collection [{0}] already exists. Aborting.'.format(TARGET_COLLECTION))
        log.debug('Please delete the target collection and try again.')
        return False
    parse_jira_xml(args, target_collection_id)


if __name__ == "__main__":
    main()
