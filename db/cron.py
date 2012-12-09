#!/usr/bin/env python3

import os
import time

from os import path
import sys
pk_path = path.normpath(path.join(path.dirname(path.abspath(__file__)), '..'))
sys.path.append(pk_path)

from db import api
from db.parse_kills import parse_kills

quiet = len(sys.argv) > 1 and sys.argv[1] == '-q'
if quiet:
	def log(*args):
		pass
else:
	log = print

log_path = path.join(pk_path, 'log')
if not path.isdir(log_path):
	os.mkdir(log_path)

timestamp = str(time.time())
last_kill_id = None
while True:
	if last_kill_id is None:
		log('querying for most recent kills')
		xml_path = path.join(log_path, timestamp + '.xml')
	else:
		log('querying for before %s...' % last_kill_id)
		xml_path = path.join(log_path, '%s-%s.xml' % (timestamp, last_kill_id))
	r = api.query(last_kill_id)
	with open(xml_path, 'w') as f:
		f.write(r.text)
	log('\tinserting...')
	last_kill_id = parse_kills(xml_path)
	if not last_kill_id:
		break
	else:
		log('\tdone')
