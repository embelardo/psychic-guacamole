#!/usr/bin/python3.6

import configparser
import pprint

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


def create_item(collection_id, title, url, tags):
    item = WEB_PAGE_TEMPLATE.copy()
    item['itemType'] = 'webpage'
    item['collections'] = [collection_id]
    item['title'] = title
    item['url'] = url
    item['websiteTitle'] = 'Jira'

    tags_list = []
    for tag in tags:
        tags_list.append({'tag': tag})
    item['tags'] = tags_list

    ret = zotero.create_items([item])
    print('create_item(): {0}'.format(ret))


def item_exists(name, tag):
    item = zotero.items(itemType='webpage', tag=tag, qmode='titleCreatorYear', q=name, limit=1)
    #print('item_exists(): {0}'.format(item))
    return True if item else False


def create_collection(name):
    if collection_exists(name) == False:
        arg = [{'name': name}]
        ret = zotero.create_collections(arg)
        # pp.pprint(ret)
        # pp.pprint(ret['success']['0'])
        return ret['success']['0']
    else:
        return None


def collection_exists(name):
    collections = zotero.all_collections()
    for collection in collections:
        if collection['data']['name'] == name:
            return True
    return False
