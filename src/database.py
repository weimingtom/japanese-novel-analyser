"""
database.py: This file handles creating the database, inserting entries
and performing queries on the data.
"""

import sqlite3

import config
from config import ALL, IGNORE
from logger import logger

"""
Open a existing database, or otherwise create a new
in its place and provide access to it
"""
class Database():

  def __init__(self, filename, tablename):
    self.filename = filename
    self.tablename = tablename
    self.fields = config.mecab_fields + 1
    self.fieldnames = [u'word']
    for i in range(config.mecab_fields):
      self.fieldnames.append(u'pos' + str(i))

  def __enter__(self):
    logger.out('connecting to database')
    self.conn = sqlite3.connect(self.filename)
    self.c = self.conn.cursor()
    self.create_table()
    self.prepare_queries()

  def create_table(self):
    # TODO: use custom tablename if possible
    sql_create = u'CREATE TABLE IF NOT EXISTS %s (freq INTEGER' % self.tablename
    for i in range(self.fields):
      sql_create = sql_create + u', ' + self.fieldnames[i] + u' TEXT'
    sql_create = sql_create + u', PRIMARY KEY ('
    for i in range(self.fields):
      sql_create = sql_create + self.fieldnames[i] + u', '
    sql_create = sql_create.rstrip(u', ')
    sql_create = sql_create + u'))'
    self.c.execute(sql_create)
    self.conn.commit()

  def prepare_queries(self):
    self.sql_up = u'UPDATE %s SET freq=freq + 1 WHERE ' % self.tablename
    self.sql_in = u'INSERT INTO %s VALUES (1' % self.tablename
    for i in range(self.fields):
      self.sql_up = self.sql_up + self.fieldnames[i] + u'=? AND '
      self.sql_in = self.sql_in + u', ?'
    self.sql_up = self.sql_up.rstrip(u' AND')
    self.sql_in = self.sql_in + u')'

  def insert_data(self, fieldvalues):
    self.c.execute(self.sql_up, fieldvalues)
    if self.c.rowcount == 0: # key does not exist, insert
      self.c.execute(self.sql_in, fieldvalues)

  def clear_table(self):
    self.c.execute(u'DELETE FROM %s' % self.tablename)
    self.conn.commit()

  """
  Selects frequences from the database. Each parameter can be
  - a specific value: Filters results to this value
  - be set to IGNORE: Combine all words that are the same on this value
  - be set to *     : No filtering
  Note that word can not be set to group.
  """
  def select(self, word, pos):
    fieldvalues = [word] + pos
    (sql, sql_sum, vals) = self.select_query(fieldvalues)
    self.c.execute(sql_sum, vals)
    result = self.c.fetchone()
    self.c.execute(sql, vals)
    return result # (fsum, rows)

  def select_results(self, amount):
    return self.c.fetchmany(amount)
  
  def select_options_query(self, fieldvalues, i):
    assert i >= 0 and i < self.fields
    sql = u'SELECT DISTINCT ' + self.fieldnames[i]
    (sql_fw, vals) = self.fromwhere_query(fieldvalues, i)
    sql = sql + sql_fw
    sql = sql + u'\nORDER BY ' + self.fieldnames[i] + u' ASC'
    return (sql, vals)

  def select_options(self, word, pos, index):
    fieldvalues = [word] + pos
    options = []
    (sql, vals) = self.select_options_query(fieldvalues, index + 1)
    self.c.execute(sql, vals)
    result = self.c.fetchall()
    for r in result:
      if r[0] != ALL:
        options.append(r[0])
    return options

  """ create the FROM WHERE part of the query """
  def fromwhere_query(self, fieldvalues, exclude=-1):
    vals = []
    sql = u'\nFROM %s \nWHERE ' % self.tablename
    for i in range(self.fields):
      if fieldvalues[i] != IGNORE and fieldvalues[i] != ALL \
          and fieldvalues[i] != u'' and exclude != i:
        sql = sql + self.fieldnames[i] + u'=? AND '
        vals.append(fieldvalues[i])
    sql = sql.rstrip(u'AND ')
    sql = sql.rstrip(u'\nWHERE ')
    return (sql, vals)

  """ create the query for frequency selection """
  def select_query(self, fieldvalues):
    sql_sum = u'SELECT sum(freq) as fsum, count(freq)'
    sql = u'SELECT sum(freq) as fsum'
    # add displayed fields
    for i in range(self.fields):
      if fieldvalues[i] != IGNORE:
        sql = sql + u', ' + self.fieldnames[i]
      else:
        sql = sql + u', "' + IGNORE + u'"'
    # add FROM WHERE query
    (sql_fw, vals) = self.fromwhere_query(fieldvalues)
    sql = sql + sql_fw
    sql_sum = sql_sum + sql_fw
    # add grouping options
    sql = sql + u'\nGROUP BY '
    for i in range(self.fields):
      if fieldvalues[i] != IGNORE:
        sql = sql + self.fieldnames[i] + u', '
    sql = sql.rstrip(u', ')
    sql = sql.rstrip(u'\nGROUP BY ')
    # add ordering
    sql = sql + u'\nORDER BY fsum DESC'
    return (sql, sql_sum, vals)
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.conn.commit()
    self.conn.close()
    logger.out('disconnected from database')

