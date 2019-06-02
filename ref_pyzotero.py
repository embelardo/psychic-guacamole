#!/usr/bin/python3.6

import pprint
from pyzotero import zotero


pp = pprint.PrettyPrinter(indent=6)

zotero = zotero.Zotero('5702932', 'user', api_key='AmVIV8y7deovLCBEE9mCRlcC')

items = zotero.items(itemType='webpage', tag='Ticket', sort='title', limit=1)

for item in items:
    pp.pprint(item)
    print('---------- ' * 5)
    print("key         : {0}".format(item['key']))
    print("title       : {0}".format(item['data']['title']))
    print("itemType    : {0}".format(item['data']['itemType']))
    print("url         : {0}".format(item['data']['url']))
    print("websiteTitle: {0}".format(item['data']['websiteTitle']))
    print("meta        : {0}".format(item['meta']))
    print("tags:")
    # pp = pprint.PrettyPrinter(indent=6)
    pp.pprint(item['data']['tags'])

print()
