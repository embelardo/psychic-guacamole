#!/usr/bin/python3.6

import os
import subprocess
import urllib.request

from contextlib import closing
from urllib.request import urlopen


patch_url = 'https://testforge.intelerad.com/hg/intelepacs/union/raw-rev/8c142a4c8aee'

# response = urllib.request.urlopen(patch_url)
# try:
#     patch_content = response.read().decode('ISO-8859-1')
#     print('Patch: {0}'.format(patch_content))
#     pid = os.getpid()
#     print('pid: {0}'.format(pid))
#     subprocess.call('lsof -p%d -iTCP' % (pid,), shell=True)
# except Exception as error:
#     log.debug(error)
#     log.debug('Error accessing URL [{0}]'.format(patch_url))

with closing(urlopen(patch_url)) as response:
    try:
        patch_content = response.read().decode('ISO-8859-1')
        print('Patch: {0}'.format(patch_content))
        pid = os.getpid()
        print('pid: {0}'.format(pid))
        subprocess.call('lsof -p%d -iTCP' % (pid,), shell=True)
    except Exception as error:
        log.debug(error)
        log.debug('Error accessing URL [{0}]'.format(patch_url))
