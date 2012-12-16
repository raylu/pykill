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
		if len(sys.argv) > 1 and sys.argv[1] in ['-q', '--quick']:
			c.execute('''
					SELECT i.typeID FROM pkItems AS i
						JOIN invTypes AS t ON i.typeID = t.typeID
						WHERE marketGroupID is NOT NULL
					UNION SELECT shipTypeID FROM pkCharacters
						JOIN invTypes ON shipTypeID = typeID
						WHERE victim AND marketGroupID is NOT NULL
				''')
		else:
			c.execute('SELECT typeID FROM invTypes WHERE marketGroupID IS NOT NULL')
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

def update_kill(kill_id):
	with conn.cursor() as c:
		c.execute('''
				SELECT cost from pkCharacters as c
				JOIN pkItemCosts AS ic ON c.shipTypeID = ic.typeID
				WHERE killId = ? AND victim
			''', (kill_id,))
		r = c.fetchone()
		if r:
			cost = r[0]
			c.nextset()
		else:
			cost = 0
		c.execute('''
				SELECT SUM(cost * (qtyDropped + qtyDestroyed)) FROM pkItems AS i
				JOIN pkItemCosts AS ic ON i.typeID = ic.typeID WHERE killID = ?
			''', (kill_id,))
		r = c.fetchone()
		if r[0]:
			cost += r[0]
		c.execute('UPDATE pkKillCosts SET cost = ? WHERE killID = ?', (cost, kill_id))

parambatch = []
for type_id in fetch_type_ids():
	value = query(type_id)
	parambatch.append((type_id, value, value))
with conn.cursor() as c:
	c.executemany('''
			INSERT INTO pkItemCosts (typeID, cost) VALUES(?, ?)
			ON DUPLICATE KEY UPDATE cost = ?
		''', parambatch)
	c.execute('SELECT killID from pkKillmails')
	while True:
		r = c.fetchone()
		if r is None:
			break
		update_kill(r[0])
