#!/usr/bin/python3.6

import configparser
import glob

from pprint import pprint

from pyzotero import zotero


# Sample webpage template
#
# {
#     'abstractNote': '',
#     'accessDate': '',
#     'collections': [],
#     'creators': [{'creatorType': 'author', 'firstName': '', 'lastName': ''}],
#     'date': '',
#     'extra': '',
#     'itemType': 'webpage',
#     'language': '',
#     'relations': {},
#     'rights': '',
#     'shortTitle': '',
#     'tags': [],
#     'title': '',
#     'url': '',
#     'websiteTitle': '',
#     'websiteType': ''
# }

TAG_TICKET_JIRA = 'ticket_jira'

config = configparser.ConfigParser()
config.read('upload_zot_items.cfg')

user_id = config['zotero_web_api']['user_id']
api_key = config['zotero_web_api']['api_key']

zotero = zotero.Zotero(user_id, 'user', api_key=api_key)

WEB_PAGE_TEMPLATE = zotero.item_template('webpage')


def upload_file_attachments(item_id, dir_name):
    item_files = glob.glob('{0}/*'.format(dir_name))
    # pprint('upload_file_attachments(): {0}'.format(item_files))
    ret = zotero.attachment_simple(item_files, item_id)
    # pprint('upload_file_attachments(): {0}'.format(ret))
    return True if not ret['failure'] else False


def create_item(collection_id, key, title, url, tags):
    item = WEB_PAGE_TEMPLATE.copy()
    item['itemType'] = 'webpage'
    item['collections'] = [collection_id]
    item['shortTitle'] = key
    item['title'] = title
    item['url'] = url
    item['websiteTitle'] = 'Jira'

    tags_list = []
    for tag in tags:
        tags_list.append({'tag': tag})
    item['tags'] = tags_list

    ret = zotero.create_items([item])
    # print('create_item(): {0}'.format(ret))
    return ret['success']['0']


def item_exists(name, tag):
    item = None
    try:
        item = zotero.items(itemType='webpage', tag=tag, qmode='titleCreatorYear', q=name, limit=1)
    except KeyError as error:
        print(error)
        return False
    #print('item_exists(): {0}'.format(item))
    return True if item else False


def create_collection(name):
    if collection_exists(name) == False:
        arg = [{'name': name}]
        ret = zotero.create_collections(arg)
        # pprint(ret)
        # pprint(ret['success']['0'])
        return ret['success']['0']
    else:
        return None


def collection_exists(name):
    collections = zotero.all_collections()
    for collection in collections:
        if collection['data']['name'] == name:
            return True
    return False
