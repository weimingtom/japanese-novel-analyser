"""
database.py: This file handles creating the database, inserting entries
and performing queries on the data.
"""

import sqlite3

import config
from config import IGNORE
from logger import logger

"""
Open a existing database, or otherwise create a new
in its place and provide access to it
"""
class Database():

  def __init__(self, filename):
    self.filename = filename
    self.fields = config.mecab_fields + 1
    self.fieldnames = ['word']
    for i in range(config.mecab_fields):
      self.fieldnames.append('pos' + str(i))

  def __enter__(self):
    logger.out('connecting to database')
    self.conn = sqlite3.connect(self.filename)
    self.c = self.conn.cursor()
    self.create_table()
    self.prepare_queries()

  def create_table(self):
    # TODO: use custom tablename if possible
    sql_create = 'CREATE TABLE IF NOT EXISTS freqs (freq INTEGER'
    for i in range(self.fields):
      sql_create = sql_create + ', ' + self.fieldnames[i] + ' TEXT'
    sql_create = sql_create + ', PRIMARY KEY ('
    for i in range(self.fields):
      sql_create = sql_create + self.fieldnames[i] + ', '
      sql_create = sql_create.rstrip(', ')
    sql_create = sql_create + '))'
    self.c.execute(sql_create)
    self.conn.commit()

  def prepare_queries(self):
    self.sql_up = 'UPDATE freqs SET freq=freq + 1 WHERE '
    self.sql_in = 'INSERT INTO freqs VALUES (1'
    for i in range(self.fields):
      self.sql_up = self.sql_up + self.fieldnames[i] + '=? AND '
      self.sql_in = self.sql_in + ', ?'
    self.sql_up = self.sql_up.rstrip(' AND')
    self.sql_in = self.sql_in + ')'

  def insert_data(self, fieldvalues):
    self.c.execute(self.sql_up, fieldvalues)
    if self.c.rowcount == 0: # key does not exist, insert
      self.c.execute(self.sql_in, fieldvalues)

  def clear_table(self):
    self.c.execute('''DELETE FROM freqs''')
    self.conn.commit()

  """
  Selects frequences from the database. Each parameter can be
  - a specific value: Filters results to this value
  - be set to IGNORE: Combine all words that are the same on this value
  - be set to *     : No filtering
  Note that word can not be set to group.
  """
  def select(self, fieldvalues, amount):
    (sql, sql_sum, vals) = self.select_query(fieldvalues)
    logger.out('executing query:\n%s\nwith values %s' % (sql, vals))
    logger.out('executing sum query:\n%s\nwith values %s' % (sql_sum, vals))
    self.c.execute(sql, vals)
    result = self.c.fetchmany(amount)
    self.c.execute(sql_sum, vals)
    fsum = self.c.fetchone()[0]
    return (result, fsum) 
  
  def select_options_query(self, fieldvalues, i):
    assert i >= 0 and i < self.fields
    sql = 'SELECT DISTINCT ' + self.fieldnames[i]
    (sql_fw, vals) = self.fromwhere_query(fieldvalues, i)
    return (sql + sql_fw, vals)

  def select_options(self, fieldvalues):
    all_options = []
    for i in range(1, self.fields): # exclude word from options
      options = []
      options.append('*')
      options.append(IGNORE)
      (sql, vals) = self.select_options_query(fieldvalues, i)
      self.c.execute(sql, vals)
      result = self.c.fetchall()
      for r in result:
        if r[0] != '*':
          options.append(r[0])
      all_options.append(options)
    return all_options

  """ create the FROM WHERE part of the query """
  def fromwhere_query(self, fieldvalues, exclude=-1):
    vals = []
    sql = '\nFROM freqs\nWHERE '
    for i in range(self.fields):
      if fieldvalues[i] != IGNORE and fieldvalues[i] != '*' \
          and fieldvalues[i] != '' and exclude != i:
        sql = sql + self.fieldnames[i] + '=? AND '
        vals.append(fieldvalues[i])
    sql = sql.rstrip('AND ')
    sql = sql.rstrip('\nWHERE ')
    return (sql, vals)

  """ create the query for frequency selection """
  def select_query(self, fieldvalues):
    sql_sum = 'SELECT sum(freq)'
    sql = sql_sum
    # add displayed fields
    for i in range(self.fields):
      if fieldvalues[i] != IGNORE:
        sql = sql + ', ' + self.fieldnames[i]
      else:
        sql = sql + ', "' + IGNORE + '"'
    # add FROM WHERE query
    (sql_fw, vals) = self.fromwhere_query(fieldvalues)
    sql = sql + sql_fw
    sql_sum = sql_sum + sql_fw
    # add grouping options
    sql = sql + '\nGROUP BY '
    for i in range(self.fields):
      if fieldvalues[i] != IGNORE:
        sql = sql + self.fieldnames[i] + ', '
    sql = sql.rstrip(', ')
    sql = sql.rstrip('\nGROUP BY ')
    # add ordering
    sql = sql + '\nORDER BY sum(freq) DESC'
    return (sql, sql_sum, vals)
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.conn.commit()
    self.conn.close()
    logger.out('disconnected from database')

