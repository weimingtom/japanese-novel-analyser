"""
database.py: This file handles creating the database, inserting entries
and performing queries on the data.
"""

import sqlite3
import os

import config
from config import ALL
from logger import logger

class Database():

  """
  Open the database in filename and use tablename as a table name prefix.
  Drop tables if drop is True, and (re-)create them if create is True.
  """
  def __init__(self, tablename):
    self.filename = os.path.join(config.get_basedir(), config.dbfile)
    self.freq_table = tablename + '_freqs'
    self.sentence_table = tablename + '_sentences'
    self.link_table = tablename + '_links'
    # data fields are the word and the parts of speech
    self.fields = config.mecab_fields + 1
    self.fieldnames = [u'word']
    for i in range(config.mecab_fields):
      self.fieldnames.append(u'pos' + str(i))

  def __enter__(self):
    logger.out('connecting to database')
    self.conn = sqlite3.connect(self.filename)
    self.c = self.conn.cursor() # Cursor for word frequency queries
    self.c2 = self.conn.cursor() # Cursor for sentence queries
    self.c3 = self.conn.cursor() # Cursor for option selections
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
    # create indices for faster lookup
    sql = 'CREATE INDEX IF NOT EXISTS freq_index ON %s (freq DESC)' % self.freq_table
    self.c.execute(sql)
    sql = 'CREATE INDEX IF NOT EXISTS len_index ON %s (len ASC)' % self.sentence_table
    self.c.execute(sql)
    jql = 'CREATE INDEX IF NOT EXISTS link_wid_index ON %s (wid ASC)' % self.link_table
    self.c.execute(sql)
    self.conn.commit()
    logger.out('created database tables')

  def prepare_queries(self):
    # prepare queries for later select, update and insert queries
    self.sql_sel = u'SELECT wid FROM %s WHERE ' % self.freq_table
    self.sql_up = u'UPDATE %s SET freq=freq + 1 WHERE wid = ?' % self.freq_table
    self.sql_in = u'INSERT INTO %s VALUES (NULL, 1' % self.freq_table
    for i in range(self.fields):
      self.sql_sel = self.sql_sel + self.fieldnames[i] + u'=? AND '
      self.sql_in = self.sql_in + u', ?'
    self.sql_sel = self.sql_sel.rstrip(u' AND')
    self.sql_in = self.sql_in + u')'

  def insert_word(self, fieldvalues):
    # insert word if new word, otherwise update frequency
    self.c.execute(self.sql_sel, fieldvalues)
    row = self.c.fetchone()
    if row == None: # word does not exist, insert
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

  def drop_table(self):
    self.c.execute(u'DROP TABLE IF EXISTS %s' % self.freq_table)
    self.c.execute(u'DROP TABLE IF EXISTS %s' % self.sentence_table)
    self.c.execute(u'DROP TABLE IF EXISTS %s' % self.link_table)
    self.conn.commit()
    logger.out('dropped database tables')

  def clear_table(self):
    self.c.execute(u'DELETE FROM %s' % self.freq_table)
    self.c.execute(u'DELETE FROM %s' % self.sentence_table)
    self.c.execute(u'DELETE FROM %s' % self.link_table)
    self.conn.commit()
    logger.out('cleared database tables')

  """
  Selects frequences from the database. The parameters can be
  set to a specific value or to string defined by config.ALL,
  in which case that parameter is ignored.
  The result is the total number of frequencies and unique number of words.
  """
  def select_frequencies(self, word, pos):
    # create query
    sql_sum = u'SELECT sum(freq), count(freq)'
    sql = u'SELECT wid, freq'
    # add displayed fields
    for i in range(self.fields):
      sql = sql + u', ' + self.fieldnames[i]
    # add FROM and WHERE part
    sql_f = u'\nFROM %s ' % self.freq_table
    (sql_w, vals) = self.where_query(word, pos)
    sql = sql + sql_f + sql_w
    sql_sum = sql_sum + sql_f + sql_w
    # add ordering
    sql = sql + u'\nORDER BY freq DESC'
    # get sum from sum query, then execute word query
    self.c.execute(sql_sum, vals)
    result = self.c.fetchone()
    self.c.execute(sql, vals)
    return result # (fsum, rows)
  
  """
  Selects sentences which contain the word with word id wid.
  """
  def select_sentences(self, wid):
    sql = u'SELECT DISTINCT sentence FROM %s NATURAL JOIN %s NATURAL JOIN %s\
            WHERE wid = ?'\
        % (self.freq_table, self.link_table, self.sentence_table)
          # ORDER BY len ASC'\
    self.c2.execute(sql, (wid,))

  """ Returns amount rows from the sentence selection """
  def select_frequency_results(self, amount):
    return self.c.fetchmany(amount)

  """ Returns amount rows from the sentence selection """
  def select_sentences_results(self, amount):
    return self.c2.fetchmany(amount)
  
  """ Selects and returns possible pos options given by the
  current configuration of word and pos values, starting from index"""
  def select_options(self, word, pos, index):
    # create the query
    sql = u'SELECT DISTINCT ' + self.fieldnames[index + 1]
    sql = sql + u'\nFROM %s ' % self.freq_table
    (sql_w, vals) = self.where_query(word, pos, index + 1)
    sql = sql + sql_w
    sql = sql + u'\nORDER BY ' + self.fieldnames[index + 1] + u' ASC'
    self.c3.execute(sql, vals)
    result = self.c3.fetchall()
    # accumulate non-generic options
    options = []
    for r in result:
      if r[0] != ALL:
        options.append(r[0])
    return options

  """ utility to create the WHERE part of a query with the given
  field values, optionally excluding one """
  def where_query(self, word, pos, exclude=-1):
    fieldvalues = [word] + pos
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
  
  def __exit__(self, typ, value, traceback):
    self.c.close()
    self.c2.close()
    self.c3.close()
    self.conn.commit()
    self.conn.close()
    logger.out('disconnected from database')

