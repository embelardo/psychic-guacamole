#!/usr/bin/python3.6

from xml.etree import ElementTree
from xml.dom import minidom
import pprint

import untangle


with open('sample.xml', 'rt') as f:
    tree = ElementTree.parse(f)

print(tree)

for item in tree.iter('item'):
    print(item)
    item_raw = ElementTree.tostring(item, 'utf-8')
    item_reparsed = minidom.parseString(item_raw)
    untangle_item = untangle.parse(item_reparsed.toprettyxml())
    print(untangle_item)
