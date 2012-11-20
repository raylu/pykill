#!/usr/bin/env python3

from xml.etree import ElementTree
import sys

if __name__ == '__main__':
	from os import path
	sys.path.append(path.normpath(path.join(path.dirname(path.abspath(__file__)), '..')))

from db import models

def parse_kill(row):
	victim = row.find('victim')
	attackers, items = row.findall('rowset')
	if attackers.get('name') != 'attackers' or items.get('name') != 'items':
		raise RuntimeError('unexpected rowsets on kill ' + row.get('killID'))

	m_kill = models.Kill(**row.attrib)
	m_kill.save()

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

if __name__ == '__main__':
	tree = ElementTree.parse(sys.argv[1])
	rows = tree.getroot().find('result').find('rowset').getchildren()
	for row in rows:
		parse_kill(row)
