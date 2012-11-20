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
	def fetch_top(cls):
		c = conn.cursor()
		c.execute('''
				SELECT k.killID, killTime,
					characterName, corporationName, allianceName, factionName,
					typeName as shipTypeName
				FROM pkKillmails AS k
				JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = true
				JOIN invTypes AS t ON c.shipTypeID = t.typeID
				ORDER BY killTime DESC
				LIMIT 50
			''')
		class expando(): pass
		while True:
			r = c.fetchone()
			if r is None:
				break
			attribs = expando()
			for i, f in enumerate(c.description):
				setattr(attribs, f[0], r[i])
			yield attribs
		c.close()

	@classmethod
	def fetch(cls, kill_id):
		c = conn.cursor()
		c.execute('''
				SELECT k.killID, killTime,
					characterName, corporationName, allianceName, factionName,
					typeName as shipTypeName
				FROM pkKillmails AS k
				JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = true
				JOIN invTypes AS t ON c.shipTypeID = t.typeID
				WHERE k.killID = ?
				ORDER BY killTime DESC
			''', (kill_id,))
		class expando(): pass
		r = c.fetchone()
		attribs = expando()
		for i, f in enumerate(c.description):
			setattr(attribs, f[0], r[i])
		c.close()
		return attribs

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
