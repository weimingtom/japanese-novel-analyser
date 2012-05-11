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
  - be set to GROUP : Combine all words that are the same on this value
  - be set to *     : No filtering
  Note that word can not be set to group.
  """
  def select(self, word, poss):
    vals = []
    sql = 'SELECT word '
    for i in range(len(poss)):
      if poss[i] != 'GROUP':
        sql = sql + 'pos' + str(i) + ' '
    sql = sql + 'FROM freqs WHERE '
    if word != '*':
      sql = sql + 'word=? AND '
      vals.append(word)
    for i in range(len(poss)):
      if poss[i] != 'GROUP' and poss[i] != '*':
        sql = sql + 'pos' + str(i) + '=? AND '
        vals.append(poss[i])
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.conn.commit()
    self.conn.close()

