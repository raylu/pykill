#!/usr/bin/env python3

import os
import requests
import sys
import time

from os import path
pk_path = path.normpath(path.join(path.dirname(path.abspath(__file__)), '..'))
sys.path.append(pk_path)

from db.parse_kills import parse_kills

key_id = 0
verification_code = ''

log_path = path.join(pk_path, 'log')
if not path.isdir(log_path):
	os.mkdir(log_path)

rs = requests.session()
timestamp = str(time.time())
last_kill_id = None
while True:
	data = {'keyID': key_id, 'vCode': verification_code}
	if last_kill_id:
		data['beforeKillID'] = last_kill_id
	if last_kill_id is None:
		print('querying for most recent kills')
		xml_path = path.join(log_path, timestamp + '.xml')
	else:
		print('querying for before %s...' % last_kill_id)
		xml_path = path.join(log_path, '%s-%s.xml' % (timestamp, last_kill_id))
	r = rs.post('https://api.eveonline.com/corp/Killlog.xml.aspx', data=data)
	with open(xml_path, 'w') as f:
		f.write(r.text)
	print('\tinserting...')
	last_kill_id = parse_kills(xml_path)
	if not last_kill_id:
		break
	else:
		print('\tdone')
