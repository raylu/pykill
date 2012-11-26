import requests

import config

rs = requests.session()

def query(before_kill_id=None):
	data = {'keyID': config.db['key_id'], 'vCode': config.db['verification_code']}
	if before_kill_id:
		data['beforeKillID'] = before_kill_id
	return rs.post('https://api.eveonline.com/corp/Killlog.xml.aspx', data=data)
