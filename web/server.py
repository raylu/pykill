#!/usr/bin/env python3

import tornado.ioloop
import tornado.web

if __name__ == '__main__':
	from os import path
	import sys
	sys.path.append(path.normpath(path.join(path.dirname(path.abspath(__file__)), '..')))

from db import models

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		kills = models.Kill.fetch_top()
		self.render('home.html', kills=kills)

class KillHandler(tornado.web.RequestHandler):
	def get(self, kill_id):
		kill = models.Kill.fetch(kill_id)
		self.render('kill.html', kill=kill)

if __name__ == "__main__":
	application = tornado.web.Application([
		(r'/', MainHandler),
		(r'/kill/([0-9]+)', KillHandler),
	], template_path='templates', debug=True)
	application.listen(8002)
	tornado.ioloop.IOLoop.instance().start()
