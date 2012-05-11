"""
database.py: This file handles creating the database, inserting entries
and performing queries on the data.
"""

import sqlite3

"""
Open a existing database, or otherwise create a new
in its place and provide access to it
"""
class Database():
  # string to use for accumulating functionality
  IGNORE = 'IGNORE'

  def __init__(self, filename, mecab_fields):
    print('creating database')
    self.filename = filename
    self.fields = mecab_fields

  def __enter__(self):
    print('connecting database')
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
  def select(self, word, pos):
    vals = []
    npresent = 0
    sql = 'SELECT sum(freq)'
    # add displayed fields
    if word != IGNORE:
      npresent = npresent + 1
      sql = sql + ', word'
    for i in range(self.fields):
      if poss[i] != IGNORE:
        npresent = npresent + 1
        sql = sql + 'pos' + str(i) + ' '
    # add equality criteria
    sql = sql + '\nFROM freqs\nWHERE '
    if word != IGNORE and word != '*':
      sql = sql + 'word=? AND '
      vals.append(word)
    for i in range(self.fields):
      if poss[i] != IGNORE and poss[i] != '*':
        sql = sql + 'pos' + str(i) + '=? AND '
        vals.append(pos[i])
    # add grouping options
    if npresent > 0:
      sql = sql + '\nGROUP BY '
      if word != IGNORE:
        sql = sql + 'word'
        npresent = npresent + 1
        sql = sql + ', word'
      for i in range(self.fields):
        if poss[i] != IGNORE:
          sql = sql + 'pos' + str(i) + ' '
    # add ordering
    sql + '\nORDER BY sum(freq)'
    logger.out('executing query:\n%s' % sql)
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.conn.commit()
    self.conn.close()

