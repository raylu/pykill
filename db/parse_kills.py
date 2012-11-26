#!/usr/bin/env python3

import oursql
import sys
from xml.etree import ElementTree

if __name__ == '__main__':
	from os import path
	sys.path.append(path.normpath(path.join(path.dirname(path.abspath(__file__)), '..')))

from db import conn, models

def parse_kills(filename):
	tree = ElementTree.parse(filename)
	error = tree.getroot().find('error')
	if error is not None:
		print('\n' + error.text)
		return
	rows = tree.getroot().find('result').find('rowset').getchildren()
	last_kill_id = None
	for row in rows:
		last_kill_id = parse_kill(row)
		if last_kill_id is None:
			return
	return last_kill_id

def parse_kill(row):
	victim = row.find('victim')
	attackers, items = row.findall('rowset')
	if attackers.get('name') != 'attackers' or items.get('name') != 'items':
		raise RuntimeError('unexpected rowsets on kill ' + row.get('killID'))

	m_kill = models.Kill(**row.attrib)
	try:
		m_kill.save()
	except oursql.IntegrityError as e:
		if e.errno != oursql.errnos['ER_DUP_ENTRY']:
			raise
		return

	m_victim = models.Character(
			killID=m_kill.killID, victim=True,
			weaponTypeID=None, finalBlow=None, securityStatus=None, damageDone=None,
			**victim.attrib
		)
	m_victim.save()

	for a in attackers:
		m_attacker = models.Character(killID=m_kill.killID, victim=False, damageTaken=None, **a.attrib)
		m_attacker.save()

	for i in items:
		m_item = models.Item(killID=m_kill.killID, **i.attrib)
		m_item.save()

	with conn.cursor() as c:
		c.execute('SELECT cost from pkItemCosts WHERE typeID = ?', (m_victim.shipTypeID,))
		r = c.fetchone()
		if r:
			cost = r[0]
			c.nextset()
		else:
			cost = 0
		c.execute('''
				SELECT SUM(cost * (qtyDropped + qtyDestroyed)) FROM pkItems AS i
				JOIN pkItemCosts AS ic ON i.typeID = ic.typeID WHERE killID = ?
			''', (m_kill.killID,))
		r = c.fetchone()
		if r[0]:
			cost += r[0]
	m_killcost = models.KillCost(killID=m_kill.killID, cost=cost)
	m_killcost.save()

	return m_kill.killID

if __name__ == '__main__':
	parse_kills(sys.argv[1])
