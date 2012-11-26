#!/usr/bin/env python3

from decimal import Decimal
from io import StringIO
import requests
from xml.etree import ElementTree

from os import path
import sys
pk_path = path.normpath(path.join(path.dirname(path.abspath(__file__)), '..'))
sys.path.append(pk_path)

from db import conn

def fetch_type_ids():
	with conn.cursor() as c:
		c.execute('''
				SELECT typeID FROM pkItems
				UNION SELECT shipTypeID FROM pkCharacters WHERE victim
			''')
		while True:
			r = c.fetchone()
			if not r:
				break
			yield r[0]

rs = requests.session()
jita_system = 30000142
def query(type_id):
	params = {'typeid': type_id, 'usesystem': jita_system}
	r = rs.get('http://api.eve-central.com/api/marketstat', params=params)
	try:
		tree = ElementTree.parse(StringIO(r.text))
	except ElementTree.ParseError:
		return 0
	value = tree.getroot().find('marketstat').find('type').find('sell').find('percentile').text
	return int(Decimal(value) * 100)

parambatch = []
for type_id in fetch_type_ids():
	value = query(type_id)
	parambatch.append((type_id, value, value))
with conn.cursor() as c:
	c.executemany('''
			INSERT INTO pkItemCosts (typeID, cost) VALUES(?, ?)
			ON DUPLICATE KEY UPDATE cost = ?
		''', parambatch)
