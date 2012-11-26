from db import conn

class BaseModel():
	def __init__(self, **kwargs):
		if kwargs.keys() != self.fields:
			raise RuntimeError('extra or missing keys: %r' % self.fields.symmetric_difference(kwargs.keys()))
		for f in self.fields:
			setattr(self, f, kwargs[f])

	def save(self):
		c = conn.cursor()
		fields = ','.join(self.__dict__.keys())
		args = ','.join('?' * len(self.fields))
		sql = 'INSERT INTO %s (%s) VALUES(%s)' % (self.table, fields, args)
		c.execute(sql, self.__dict__.values())
		c.close()

	def __str__(self):
		return '%s %s' % (self.__class__, self.__dict__)

class Kill(BaseModel):
	table = 'pkKillmails'
	fields = frozenset([
			'killID',
			'solarSystemID',
			'killTime',
			'moonID',
		])

	@classmethod
	def count(cls):
		with conn.cursor() as c:
			c.execute('SELECT COUNT(killID) FROM pkKillmails')
			return c.fetchone()[0]

	@classmethod
	def fetch_list(cls, offset, count):
		c = conn.cursor()
		c.execute('''
				SELECT k.killID, killTime,
					characterName, corporationID, corporationName, allianceID, allianceName,
					shipTypeID, typeName as shipTypeName, cost
				FROM pkKillmails AS k
				JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = true
				JOIN invTypes AS t ON c.shipTypeID = t.typeID
				JOIN pkKillCosts AS kc ON k.killID = kc.killID
				ORDER BY killTime DESC
				LIMIT ?, ?
			''', (offset, count))
		while True:
			attribs = objectify(c)
			if attribs is None:
				break
			yield attribs
		c.close()

	@classmethod
	def fetch(cls, kill_id):
		with conn.cursor() as c:
			c.execute('''
					SELECT
						killTime, characterID, characterName,
						corporationID, corporationName, allianceID, allianceName,
						t.typeID as shipTypeID, typeName as shipTypeName,
						groupName, ic.cost as shipCost, damageTaken,
						s.solarSystemName as systemName, s.security as systemSecurity
					FROM pkKillmails AS k
					JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = true
					JOIN invTypes AS t ON c.shipTypeID = t.typeID
					LEFT JOIN pkItemCosts AS ic ON c.shipTypeID = ic.typeID
					JOIN invGroups as g ON t.groupID = g.groupID
					JOIN mapSolarSystems as s ON k.solarSystemID = s.solarSystemID
					WHERE k.killID = ?
				''', (kill_id,))
			return objectify(c)

class Character(BaseModel):
	table = 'pkCharacters'
	fields = frozenset([
			'characterID',
			'killID',
			'victim',
			'characterID',
			'characterName',
			'shipTypeID',
			'allianceID',
			'allianceName',
			'corporationID',
			'corporationName',
			'factionID',
			'factionName',
			'damageTaken',
			'damageDone',
			'finalBlow',
			'securityStatus',
			'weaponTypeID',
		])

	@classmethod
	def fetch_attackers(cls, kill_id):
		with conn.cursor() as c:
			c.execute('''
					SELECT
						characterID, characterName, finalBlow,
						corporationID, corporationName, allianceID, allianceName,
						damageDone, securityStatus,
						shipTypeID, t1.typeName as shipTypeName,
						weaponTypeID, t2.typeName as weaponTypeName
					FROM pkCharacters AS c
					JOIN invTypes AS t1 ON c.shipTypeID = t1.typeID
					JOIN invTypes AS t2 ON c.weaponTypeID = t2.typeID
					WHERE c.killID = ? AND c.victim = false
					ORDER BY c.finalBlow DESC, c.damageDone DESC
				''', (kill_id,))
			while True:
				attribs = objectify(c)
				if attribs is None:
					break
				yield attribs

class Item(BaseModel):
	table = 'pkItems'
	fields = frozenset([
			'typeID',
			'killID',
			'flag',
			'qtyDropped',
			'qtyDestroyed',
			'singleton',
		])

	@classmethod
	def fetch(cls, kill_id):
		with conn.cursor() as c:
			c.execute('''
					SELECT
						i.typeID as typeID, typeName, categoryID,
						flag, qtyDropped, qtyDestroyed, singleton, ic.cost
					FROM pkItems as i
					JOIN invTypes AS t ON i.typeID = t.typeID
					JOIN pkItemCosts AS ic ON i.typeID = ic.typeID
					JOIN invGroups AS g ON t.groupID = g.groupID
					WHERE i.killID = ?
					ORDER BY flag DESC, qtyDropped + qtyDestroyed ASC
				''', (kill_id,))
			while True:
				attribs = objectify(c)
				if attribs is None:
					break
				yield attribs

class KillCost(BaseModel):
	table = 'pkKillCosts'
	fields = frozenset([
			'killID',
			'cost',
		])

class DBRow:
	def __str__(self):
		return '<DBRow>: ' + str(self.__dict__)

def objectify(cursor):
	r = cursor.fetchone()
	if r is None:
		return
	attribs = DBRow()
	for i, f in enumerate(cursor.description):
		setattr(attribs, f[0], r[i])
	return attribs
