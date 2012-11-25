#!/usr/bin/env python3

import tornado.ioloop
import tornado.web

from os import path
import sys
pk_path = path.normpath(path.join(path.dirname(path.abspath(__file__)), '..'))
sys.path.append(pk_path)

from db import models

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.redirect('/page/1')

class ListHandler(tornado.web.RequestHandler):
	page_size = 50

	def get(self, page):
		page = int(page)
		max_page_f = models.Kill.count() / self.page_size
		max_page = int(max_page_f)
		if max_page_f != max_page:
			max_page += 1
		kills = models.Kill.fetch_top((page-1) * self.page_size, self.page_size)
		self.render('list.html', kills=kills, page={'current': page, 'max': max_page})

class KillHandler(tornado.web.RequestHandler):
	def get(self, kill_id):
		kill = models.Kill.fetch(kill_id)
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
