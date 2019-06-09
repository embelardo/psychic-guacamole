#!/usr/bin/python3.6

import re

from datetime import datetime


date_string = 'Wed, 22 May 2019 13:40:38 -0400'

regex = re.compile(r'[\w]+, ([\d]+) ([\w]+) ([\d]+) .*')
search_obj = regex.search(date_string)

day = search_obj.group(1)
month = search_obj.group(2)
year = search_obj.group(3)

print('Group 1: {0}'.format(day))
print('Group 2: {0}'.format(month))
print('Group 3: {0}'.format(year))

print('Raw Date: %s %s %s' % (day.zfill(2), month, year))

# Group 1: 22
# Group 2: May
# Group 3: 2019
# Date: 22 May 2019

datetime_obj = datetime.strptime('%s %s %s' % (day.zfill(2), month, year), '%d %b %Y')

print('Formatted Date: circa_{0}'.format(datetime_obj.strftime('%m%d_%Y')))
print('Formatted Date: circa_{0}'.format(datetime_obj.strftime('%Y_%m%d')))
