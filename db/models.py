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
	def fetch_top(cls, offset, count):
		c = conn.cursor()
		c.execute('''
				SELECT k.killID, killTime,
					characterName, corporationName, allianceName, factionName,
					typeName as shipTypeName
				FROM pkKillmails AS k
				JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = true
				JOIN invTypes AS t ON c.shipTypeID = t.typeID
				ORDER BY killTime DESC
				LIMIT ?, ?
			''', (offset, count))
		while True:
			attribs = cls.objectify(c)
			if attribs is None:
				break
			yield attribs
		c.close()

	@classmethod
	def fetch(cls, kill_id):
		with conn.cursor() as c:
			c.execute('''
					SELECT killTime,
						characterID, characterName, corporationName, allianceName, factionName,
						t.typeID as shipTypeID, typeName as shipTypeName, damageTaken,
						s.solarSystemName as systemName, s.security as systemSecurity
					FROM pkKillmails AS k
					JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = true
					JOIN invTypes AS t ON c.shipTypeID = t.typeID
					JOIN mapSolarSystems as s ON k.solarSystemID = s.solarSystemID
					WHERE k.killID = ?
				''', (kill_id,))
			kill = cls.objectify(c)
			c.nextset()

			c.execute('''
					SELECT
						characterID, characterName, corporationName, allianceName, factionName,
						damageDone, securityStatus,
						t1.typeName as shipTypeName, t2.typeName as weaponTypeName
					FROM pkKillmails AS k
					JOIN pkCharacters AS c ON k.killID = c.killID and c.victim = false
					JOIN invTypes AS t1 ON c.shipTypeID = t1.typeID
					JOIN invTypes AS t2 ON c.weaponTypeID = t2.typeID
					WHERE k.killID = ?
					ORDER BY c.finalBlow DESC
				''', (kill_id,))
			attackers = []
			while True:
				attribs = cls.objectify(c)
				if attribs is None:
					break
				attackers.append(attribs)

			c.execute('''
					SELECT i.typeID as typeID, typeName, flag, qtyDropped, qtyDestroyed, singleton
					FROM pkItems as i
					JOIN invTypes AS t ON i.typeID = t.typeID
					WHERE i.killID = ?
					ORDER BY flag
				''', (kill_id,))
			items = []
			while True:
				attribs = cls.objectify(c)
				if attribs is None:
					break
				items.append(attribs)

		kill.attackers = attackers
		kill.items = items
		return kill

	@classmethod
	def objectify(cls, cursor):
		r = cursor.fetchone()
		if r is None:
			return
		class expando(): pass
		attribs = expando()
		for i, f in enumerate(cursor.description):
			setattr(attribs, f[0], r[i])
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
