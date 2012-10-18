import MySQLdb
import logging

def init_db(server, user, pwd, name):
	return MySQLdb.connect(server, user, pwd, name)

def db_read(db, sql):
	try:
		logging.debug(sql)
		cursor = db.cursor()
		cursor.execute(sql)
		return cursor.fetchall()
	except Exception as e:
		logging.warning("Warning: unable to exec: <%s>: %s", sql, e)

def db_modify(db, sql, debug=False):
	try:
		logging.debug(sql)
		if not debug:
			cursor = db.cursor()
			cursor.execute(sql)
			db.commit()
			return cursor.lastrowid
	except Exception as e:
		logging.warning("Warning: unable to exec: <%s>: %s", sql, e)
		db.rollback()

def db_close(db):
	db.close