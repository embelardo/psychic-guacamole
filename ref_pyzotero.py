#!/usr/bin/python3.6

import configparser
import pprint

from pyzotero import zotero


config = configparser.ConfigParser()
config.read('upload_zot_items.cfg')

pp = pprint.PrettyPrinter(indent=6)

user_id = config['zotero_web_api']['user_id']
api_key = config['zotero_web_api']['api_key']

zotero = zotero.Zotero(user_id, 'user', api_key=api_key)


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


def get_all_collections():
    collections = zotero.all_collections()
    print('All my collections')
    for collection in collections:
        pp.pprint(collection['data'])


def get_webpage_item_template():
    webpage_template = zotero.item_template('webpage')
    print('WebPage template for creating new item')
    print()
    pp.pprint(webpage_template)


def search_for_items():
    items = zotero.items(itemType='webpage', tag='Ticket', sort='title', limit=1)

    for item in items:
        print()
        pp.pprint(item)
        print('---------- ' * 5)
        print("key         : {0}".format(item['key']))
        print("title       : {0}".format(item['data']['title']))
        print("itemType    : {0}".format(item['data']['itemType']))
        print("url         : {0}".format(item['data']['url']))
        print("websiteTitle: {0}".format(item['data']['websiteTitle']))
        print("meta        : {0}".format(item['meta']))
        print("tags:")

        pp.pprint(item['data']['tags'])
        print('---------- ' * 5)


if __name__ == "__main__":
    # search_for_items()
    # get_webpage_item_template()
    # get_all_collections()

    # collection_name = 'uploaded_jira_tickets'
    # collection = collection_exists(collection_name)
    # if collection:
    #     pp.pprint(collection)
    # else:
    #     print('collection [{0}] does not exist.'.format(collection_name))

    #collection_name = 'uploaded_jira_tickets'
    #print(create_collection(collection_name))

    print('item_exists(): {0}'.format(item_exists('The SQ4R Method of Study', 'Note')))
