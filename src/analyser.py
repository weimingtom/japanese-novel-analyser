#!/usr/bin/env python2

"""
This is the Japanese Novel Analyser.
It reads in novels from files in aozora formatting, strips this formatting,
invokes the mecab morphological analysis and counts word frequencies.
Then it stores them in a database for later use. Repeated invokations
add to the existing frequencies, unless the switch --droptable is given.

Usage: analyser.py [OPTION]... FILE..
Read and analyse each FILE.

Options:
  -h, --help          Display this help
  -e, --encoding=ENC  Set the encoding for the files to ENC
  -r, --recursive     Read files in all folders recursively
  -t, --tablename     Table to use (will be created if not existing)
  -f, --format=FORMAT Set the format of the files;
                      FORMAT is  'plain', 'aozora' or 'html`
  -d, --droptable     Drop table before creating and filling it
"""

import sys
import getopt
import codecs
import os.path
import sqlite3
import re

import formats
import mecab
import freq
import database
import config
from logger import logger

def main():
  basedir = config.get_basedir()
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hf:e:o:rdt:', ['help','format=','encoding=', 'droptable', 'recursive', 'tablename='])
  except getopt.error as opterr:
    logger.err(opterr)
    logger.err('for help use --help')
    sys.exit(2)
  # process config and options
  formatter = config.formatter
  encoding = config.encoding
  tablename = config.tablename
  drop = False
  recursive = False
  for o, a in opts:
    if o in ('-h', '--help'):
      logger.out(__doc__)
      sys.exit(0)
    if o in ('-f', '--format'):
      formatter = a
      if formatter not in ('plain', 'aozora', 'html'):
        logger.err('format not supported: %s' % formatter)
        sys.exit(2)
    if o in ('-e', '--encoding'):
      encoding = a
      try:
        codecs.lookup(encoding)
      except LookupError:
        logger.err('encoding not found: %s' % encoding)
        sys.exit(2)
    if o in ('-d', '--droptable'):
      drop = True
    if o in ('-t', '--tablename'):
      tablename = a
      if not re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', tablename):
        logger.err('invalid table name: %s' % tablename)
        sys.exit(2)
    if o in ('-r', '--recursive'):
      recursive = True
  # create formatter and parser
  if(formatter == 'aozora'):
    formatter = formats.AozoraFormat()
  elif(formatter == 'html'):
    formatter = formats.HTMLFormat()
  else:
    formatter = formats.Format()
  parser = mecab.PyMeCab()
  # access database
  try:
    db = database.Database(tablename)
    with db:
      if(drop):
        db.drop_table()
      db.create_table()
      # process files
      logger.out('analyzing text files')
      if recursive:
        for dirname in args:
          for dirpath, dirs, files in os.walk(dirname):
            logger.out('going through directory %s' % dirpath)
            for filename in files:
              analyze(os.path.join(dirpath, filename), formatter, parser, encoding, db)
      else:
        for filename in args:
          analyze(filename, formatter, parser, encoding, db)
      logger.out('done analyzing')
  except sqlite3.Error as e:
    logger.err('database error: %s' % e)

def analyze(filename, formatter, parser, encoding, db):
  logger.out('reading %s' % filename)
  formatter.new_file()
  try:
    fp = codecs.open(filename, 'r', encoding)
  except IOError as e:
    logger.err('error opening %s: %s' % (filename, e))
  else:
    with fp:
      # process all files line by line
      for line in fp:
        trimmed_line = formatter.trim(line)
        mecab_data = parser.parse(trimmed_line, db)

if __name__ == '__main__':
  main()

