#coding:utf8
import MySQLdb
import tornado.options

from tornado.options import define, options

define("mysql_host",default = "127.0.0.1", help = "db host")
define("mysql_user",default = "root", help = "db user")
define("mysql_password", default = "", help = "db password (default null)")
define("mysql_port", default = "13306", help = "db port")

class MysqlQuery():
	def __init__(self):
#		self.sqlComannd = sqlCommand
		pass;

	def query(self,sqlCommand):
		tornado.options.parse_command_line()
		conn = MySQLdb.connect(
			host = options.mysql_host,
			user = options.mysql_user,
			port = 13306,
			passwd = options.mysql_password
		)
		cur=conn.cursor()
		cur.execute(sqlCommand)
		ret = ''
		ret = cur.fetchall()
		return  list(ret)
		cur.close()
		debug = True

#class MysqlQuery(MySQL_Conn):
#	def __init__(self,sqlCommand):
#		self.sqlCommand = sqlCommand
#
#	def query(self):
#		ret = ''
#		ret = MySQL_Conn.query(self,self.sqlCommand)
#		return ret

#t = MysqlQuery('show status;')
#print t.query()

class LangMysqlQuery(MysqlQuery):
	def __init__(self):
		pass;
	def langQuery(self,langSqlCommand):
		spite


#t = MysqlQuery()
#print t.query('select a,b from test.draw')
