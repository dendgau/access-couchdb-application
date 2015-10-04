# -*- coding: utf-8 -*-
import pycouchdb
import logging


class ConnectCouchdb(object):
	server = None
	database = None

	def __init__(self, server_name="http://admin:admin@127.0.0.1:5984", database_name="example"):
		try:
			self.server = pycouchdb.Server(server_name)
			self.get_database(database_name)
		except Exception, e:
			logging.error(str(e))
			raise

	def get_database(self, database_name):
		try:
			self.database = self.server.database(database_name)
		except Exception, e:
			logging.error(str(e))
			raise

	def save_doc(self, _doc):
		try:
			return self.database.save(_doc)
		except Exception, e:
			logging.error(str(e))
			raise

	def get_doc(self, _id):
		try:
			return self.database.get(_id)
		except Exception, e:
			logging.error(str(e))
			raise

	def delete_doc(self, _id):
		try:
			return self.database.delete(_id)
		except Exception, e:
			logging.error(str(e))
			raise

	def query_doc(self, _map_func=None):
		try:
			return list(self.database.temporary_query(_map_func))
		except Exception, e:
			logging.error(str(e))
			raise


