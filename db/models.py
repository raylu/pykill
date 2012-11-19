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
