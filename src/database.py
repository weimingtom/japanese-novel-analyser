"""
database.py: This file handles creating the database, inserting entries
and performing queries on the data.
"""

import sqlite3

import config
from config import ALL
from logger import logger

"""
Open a existing database, or otherwise create a new
in its place and provide access to it
"""
class Database():

  def __init__(self, filename, tablename, clear=False, create=False):
    self.filename = filename
    self.freq_table = tablename + '_freqs'
    self.sentence_table = tablename + '_sentences'
    self.link_table = tablename + '_links'
    self.clear = clear
    self.create = create
    self.fields = config.mecab_fields + 1
    self.fieldnames = [u'word']
    for i in range(config.mecab_fields):
      self.fieldnames.append(u'pos' + str(i))

  def __enter__(self):
    logger.out('connecting to database')
    self.conn = sqlite3.connect(self.filename)
    self.c = self.conn.cursor() # Cursor for frequences
    self.c2 = self.conn.cursor() # Cursor for sentences
    self.c3 = self.conn.cursor() # Cursor for selections
    if self.clear:
      self.clear_table()
      logger.out('cleared database tables')
    if self.create:
      self.create_table()
      logger.out('created database tables')
    self.prepare_queries()

  def create_table(self):
    # create freq table
    sql = u'CREATE TABLE IF NOT EXISTS %s ( \
        wid INTEGER PRIMARY KEY, freq INTEGER' % self.freq_table
    for i in range(self.fields):
      sql = sql + u', ' + self.fieldnames[i] + u' TEXT'
    sql = sql + u', UNIQUE ('
    for i in range(self.fields):
      sql = sql + self.fieldnames[i] + u', '
    sql = sql.rstrip(u', ')
    sql = sql + u'))'
    self.c.execute(sql)
    # create sentence table
    sql = u'CREATE TABLE IF NOT EXISTS %s ( \
        sid INTEGER PRIMARY KEY, sentence TEXT, len INTEGER)' % self.sentence_table
    self.c.execute(sql)
    # create link table
    sql = u'CREATE TABLE IF NOT EXISTS %s ( \
        wid INTEGER, sid INTEGER, \
        FOREIGN KEY(wid) REFERENCES %s(wid), \
        FOREIGN KEY(sid) REFERENCES %s(sid))'\
        % (self.link_table, self.freq_table, self.sentence_table)
    self.c.execute(sql)
    # create index for freq
    sql = 'CREATE INDEX IF NOT EXISTS freq_index ON %s (freq DESC)' % self.freq_table
    self.c.execute(sql)
    self.conn.commit()

  def prepare_queries(self):
    self.sql_sel = u'SELECT wid FROM %s WHERE ' % self.freq_table
    self.sql_up = u'UPDATE %s SET freq=freq + 1 WHERE wid = ?' % self.freq_table
    self.sql_in = u'INSERT INTO %s VALUES (NULL, 1' % self.freq_table
    for i in range(self.fields):
      self.sql_sel = self.sql_sel + self.fieldnames[i] + u'=? AND '
      self.sql_in = self.sql_in + u', ?'
    self.sql_sel = self.sql_sel.rstrip(u' AND')
    self.sql_in = self.sql_in + u')'

  def insert_word(self, fieldvalues, sentence):
    self.c.execute(self.sql_sel, fieldvalues)
    row = self.c.fetchone()
    if row == None: # key does not exist, insert
      self.c.execute(self.sql_in, fieldvalues)
      return self.c.lastrowid
    else: # update
      wid = row[0]
      self.c.execute(self.sql_up, (wid,))
      return wid
  
  def insert_sentence(self, sentence):
    sql = u'INSERT INTO %s VALUES (NULL, ?, ?)' % self.sentence_table
    self.c.execute(sql, (sentence,len(sentence)))
    return self.c.lastrowid

  def insert_link(self, word_id, sentence_id):
    sql = u'INSERT INTO %s VALUES (?, ?)' % self.link_table
    self.c.execute(sql, (word_id, sentence_id))

  def clear_table(self):
    self.c.execute(u'DROP TABLE IF EXISTS %s' % self.freq_table)
    self.c.execute(u'DROP TABLE IF EXISTS %s' % self.sentence_table)
    self.c.execute(u'DROP TABLE IF EXISTS %s' % self.link_table)
    self.conn.commit()

  """
  Selects frequences from the database. Each parameter can be
  - a specific value: Filters results to this value
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
  
  def select_sentences(self, wid):
    sql = u'SELECT DISTINCT sentence FROM %s NATURAL JOIN %s NATURAL JOIN %s\
            WHERE wid = ?\
            ORDER BY len ASC'\
        % (self.freq_table, self.link_table, self.sentence_table)
    self.c2.execute(sql, (wid,))

  def select_sentences_results(self, amount):
    return self.c2.fetchmany(amount)

  def select_results(self, amount):
    return self.c.fetchmany(amount)
  
  def select_options_query(self, fieldvalues, i):
    assert i >= 0 and i < self.fields
    sql = u'SELECT DISTINCT ' + self.fieldnames[i]
    sql = sql + u'\nFROM %s ' % self.freq_table
    (sql_w, vals) = self.where_query(fieldvalues, i)
    sql = sql + sql_w
    sql = sql + u'\nORDER BY ' + self.fieldnames[i] + u' ASC'
    return (sql, vals)

  def select_options(self, word, pos, index):
    fieldvalues = [word] + pos
    options = []
    (sql, vals) = self.select_options_query(fieldvalues, index + 1)
    self.c3.execute(sql, vals)
    result = self.c3.fetchall()
    for r in result:
      if r[0] != ALL:
        options.append(r[0])
    return options

  """ create the WHERE part of the query """
  def where_query(self, fieldvalues, exclude=-1):
    vals = []
    sql = '\nWHERE '
    for i in range(self.fields):
      if fieldvalues[i] != ALL \
          and fieldvalues[i] != u'' and exclude != i:
        sql = sql + self.fieldnames[i] + u'=? AND '
        vals.append(fieldvalues[i])
    sql = sql.rstrip(u'AND ')
    sql = sql.rstrip(u'\nWHERE ')
    return (sql, vals)

  """ create the query for frequency selection """
  def select_query(self, fieldvalues):
    sql_sum = u'SELECT sum(freq), count(freq)'
    sql = u'SELECT wid, freq'
    # add displayed fields
    for i in range(self.fields):
      sql = sql + u', ' + self.fieldnames[i]
    # add FROM and WHERE part
    sql_f = u'\nFROM %s ' % self.freq_table
    (sql_w, vals) = self.where_query(fieldvalues)
    sql = sql + sql_f + sql_w
    sql_sum = sql_sum + sql_f + sql_w
    # add ordering
    sql = sql + u'\nORDER BY freq DESC'
    return (sql, sql_sum, vals)
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.conn.commit()
    self.conn.close()
    logger.out('disconnected from database')

