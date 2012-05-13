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
    self.fields = config.mecab_fields

  def __enter__(self):
    logger.out('connecting to database')
    self.conn = sqlite3.connect(self.filename)
    self.c = self.conn.cursor()
    self.create_table()
    self.prepare_queries()

  def create_table(self):
    # TODO: use custom tablename if possible
    sql_create = 'CREATE TABLE IF NOT EXISTS freqs (freq INTEGER, word TEXT'
    for i in range(self.fields):
      sql_create = sql_create + ', pos' + str(i) + ' TEXT'
    sql_create = sql_create + ', PRIMARY KEY (word'
    for i in range(self.fields):
      sql_create = sql_create + ', pos' + str(i)
    sql_create = sql_create + '))'
    self.c.execute(sql_create)
    self.conn.commit()

  def prepare_queries(self):
    self.sql_up = 'UPDATE freqs SET freq=freq + 1 WHERE word=?'
    self.sql_in = 'INSERT INTO freqs VALUES (1, ?'
    for i in range(self.fields):
      self.sql_up = self.sql_up + ' AND pos' + str(i) + '=?'
      self.sql_in = self.sql_in + ', ?'
    self.sql_in = self.sql_in + ')'

  def insert_data(self, word_data):
    key = [word_data.word] + word_data.pos
    self.c.execute(self.sql_up, key)
    if self.c.rowcount == 0: # key does not exist, insert
      self.c.execute(self.sql_in, key)

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
  def select(self, word, pos, amount):
    (sql, sql_sum, vals) = self.select_query(word, pos)
    logger.out('executing query:\n%s\nwith values %s' % (sql, vals))
    logger.out('executing sum query:\n%s\nwith values %s' % (sql_sum, vals))
    self.c.execute(sql, vals)
    result = self.c.fetchmany(amount)
    self.c.execute(sql_sum, vals)
    fsum = self.c.fetchone()[0]
    return (result, fsum) 
  
  def select_options_query(self, word, pos, pos_i):
    assert pos_i >= 0 and pos_i < config.mecab_fields
    vals = []
    sql = 'SELECT DISTINCT pos' + str(pos_i) + ' FROM freqs'
    # add equality criteria TODO: create function
    sql = sql + '\nWHERE'
    if word != IGNORE and word != '*':
      sql = sql + 'word=? AND '
      vals.append(word)
    for i in range(self.fields):
      if pos[i] != IGNORE and pos[i] != '*':
        sql = sql + 'pos' + str(i) + '=? AND '
        vals.append(pos[i])
    sql = sql.rstrip('AND ')
    if(len(vals) == 0):
      sql_eq = sql_eq.rstrip('\nWHERE')
    return (sql, vals)

  def select_options(self, word, pos):
    all_options = []
    selmax = 0
    ignmin = config.mecab_fields
    for i in range(config.mecab_fields):
      all_options.append([])
      if pos[i] == 'IGNORE':
        if i > 0 and ignmin > i:
          all_options[i - 1].append('IGNORE')
        ignmin = i + 1
      elif pos[i] != '*':
        selmax = i + 1
      if i < ignmin:
        all_options[i].append('*')
      if i <= selmax: # append part of speech options
        (sql, vals) = select_options_query(word, pos, i)
        self.c.execute(sql, vals)
        result = self.c.fetchall()
        for r in result:
          all_options[i].append(r[0])
      if i >= ignmin - 1:
        all_options[i].append('IGNORE')

  def select_query(self, word, pos):
    vals = []
    npresent = 0
    sql_sum = 'SELECT sum(freq)'
    sql = sql_sum
    # add displayed fields
    if word != IGNORE:
      npresent = npresent + 1
      sql = sql + ', word'
    for i in range(self.fields):
      if pos[i] != IGNORE:
        npresent = npresent + 1
        sql = sql + ', pos' + str(i)
    # add equality criteria
    sql_eq = '\nFROM freqs\nWHERE '
    if word != IGNORE and word != '*':
      sql_eq = sql_eq + 'word=? AND '
      vals.append(word)
    for i in range(self.fields):
      if pos[i] != IGNORE and pos[i] != '*':
        sql_eq = sql_eq + 'pos' + str(i) + '=? AND '
        vals.append(pos[i])
    sql_eq = sql_eq.rstrip('AND ')
    if(len(vals) == 0):
      sql_eq = sql_eq.rstrip('\nWHERE')
    sql = sql + sql_eq
    sql_sum = sql_sum + sql_eq
    # add grouping options
    if npresent > 0:
      sql = sql + '\nGROUP BY '
      if word != IGNORE:
        sql = sql + 'word, '
      for i in range(self.fields):
        if pos[i] != IGNORE:
          sql = sql + 'pos' + str(i) + ', '
      sql = sql.rstrip(', ')
    # add ordering
    sql = sql + '\nORDER BY sum(freq) DESC'
    return (sql, sql_sum, vals)
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.conn.commit()
    self.conn.close()
    logger.out('disconnected from database')

