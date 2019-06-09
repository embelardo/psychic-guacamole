#!/usr/bin/python3.6

import configparser
import pprint

from pyzotero import zotero


config = configparser.ConfigParser()
config.read('upload_zot_items.cfg')

user_id = config['zotero_web_api']['user_id']
api_key = config['zotero_web_api']['api_key']

zotero = zotero.Zotero(user_id, 'user', api_key=api_key)


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
