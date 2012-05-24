#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
This is the Frequency Browser
It uses the database created by the Japanese Novel Analyser and
allows displaying the frequencies by selecting certain parts of speech
or conjugations. For these it has grouping and filter options.

Usage: freqbrowser.py [OPTION]... FILTER...
Display the frequencies with the given FILTERs

-n, --number=N   Display the top N frequencies in list
-t, --tablename  Table to use
"""

import sys
import getopt
import os.path
import sqlite3
import re

import database
import config
import gui
from logger import logger

def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hn:t:', ['help','number=','tablename='])
  except getopt.error as opterr:
    logger.err(opterr)
    logger.err('for help use --help')
    sys.exit(2)
  # process config and options
  list_number = config.list_number
  tablename = config.tablename
  for o, a in opts:
    if o in ('-h', '--help'):
      logger.out(__doc__)
      sys.exit(0)
    if o in ('-n', '--number'):
      try:
        top_number = int(a)
      except ValueError:
        logger.err('invalid argument for top number: %s' % a)
        sys.exit(2)
      if list_number <= 0:
        logger.err('invalid top number: %s' % list_number)
        sys.exit(2)
    if o in ('-t', '--tablename'):
      tablename = a
      if not re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', tablename):
        logger.err('invalid table name: %s' % tablename)
        sys.exit(2)
  # create formatter and parser
  try:
    db = database.Database(tablename)
    with db:
      display_gui(db, list_number)
  except sqlite3.Error as e:
    logger.err('database error: %s' % e)

def display_gui(db, listsize):
  ui = gui.FreqGUI(db, listsize)
  ui.show()

if __name__ == '__main__':
  main()
