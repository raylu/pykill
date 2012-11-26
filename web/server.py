#!/usr/bin/env python3

from collections import defaultdict
import datetime
import tornado.ioloop
import tornado.web

from os import path
import sys
pk_path = path.normpath(path.join(path.dirname(path.abspath(__file__)), '..'))
sys.path.append(pk_path)

from db import models

class RequestHandler(tornado.web.RequestHandler):
	def render_string(self, template_name, **kwargs):
		s = super(RequestHandler, self).render_string(template_name, **kwargs)
		return s.replace(b'\n', b'') # this is like Django's {% spaceless %}

class MainHandler(RequestHandler):
	def get(self):
		self.redirect('/page/1')

class ListHandler(RequestHandler):
	page_size = 50

	def get(self, page):
		page = int(page)
		max_page_f = models.Kill.count() / self.page_size
		max_page = int(max_page_f)
		if max_page_f != max_page:
			max_page += 1
		kills = models.Kill.fetch_top((page-1) * self.page_size, self.page_size)
		self.render('list.html', kills=kills, page={'current': page, 'max': max_page})

class KillHandler(RequestHandler):
	def get(self, kill_id):
		kill = models.Kill.fetch(kill_id)
		kill.attackers = models.Character.fetch_attackers(kill_id)
		items = defaultdict(dict)
		for item in models.Item.fetch(kill_id):
			if 27 <= item.flag <= 34:
				slot = 'High' 
			elif 19 <= item.flag <= 26:
				slot = 'Medium' 
			elif 11 <= item.flag <= 18:
				slot = 'Low' 
			elif 92 <= item.flag <= 99:
				slot = 'Rig' 
			elif item.flag == 87:
				slot = 'Drone Bay' 
			elif item.flag == 5:
				slot = 'Cargo' 
			elif item.flag == 89:
				slot = 'Implant' 
			else:
				raise RuntimeError('unknown flag: %r' % item.flag)
			item.ammo = (item.categoryID == 8 and slot != 'Cargo') # 8 = Charge
			if item.typeID in items[slot]:
				items[slot][item.typeID].qtyDropped += item.qtyDropped
				items[slot][item.typeID].qtyDestroyed += item.qtyDestroyed
			else:
				items[slot][item.typeID] = item
		kill.items = items
		ago = datetime.datetime.now() - kill.killTime
		if ago.days < 2:
			kill.ago = '%s hours' % round(ago.days * 24 + ago.seconds / (60 * 60), 1)
		else:
			kill.ago = '%s days' % round(ago.days + ago.seconds / (60 * 60 * 24), 1)
		self.render('kill.html', kill=kill)

if __name__ == "__main__":
	template_path = path.join(pk_path, 'web', 'templates')
	application = tornado.web.Application([
		(r'/', MainHandler),
		(r'/page/([0-9]+)', ListHandler),
		(r'/kill/([0-9]+)', KillHandler),
	], template_path=template_path, debug=True)
	application.listen(8002)
	tornado.ioloop.IOLoop.instance().start()
