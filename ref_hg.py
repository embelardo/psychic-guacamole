#!/usr/local/bin/python3

import hglib

rev = '9b6067ef2a7c'


client = hglib.open('/Users/miko/evolve-repos/master-pirates')

revs = int(client.tip().rev)
files = len(list(client.manifest()))

print('Revisions   : {0}'.format(revs))
print('Files       : {0}'.format(files))

diff_content = client.diff(revs=[], change=rev, showfunction=True, ignoreallspace=True, unified=5, subrepos=False)
print('diff_content: {0}'.format(diff_content))

f = open('{0}.patch.txt'.format(rev), 'w')
f.write(diff_content.decode('ISO-8859-1'))
f.close()
