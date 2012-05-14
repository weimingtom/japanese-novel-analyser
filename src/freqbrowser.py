#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
This is the Frequency Browser
It uses the database created by the Japanese Novel Analyser and
allows displaying the frequencies by selecting certain parts of speech
or conjugations. For these it has grouping and filter options.

Usage: freqbrowser.py [OPTION]... FILTER...
Display the frequencies with the given FILTERs

-n, --number=N   Display the top N frequencies
"""

import sys
import getopt
import os.path
import sqlite3

import database
import config
import gui
from logger import logger

def main():
  # get path of main program directory
  basedir = config.get_basedir()
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hn:', ['help','number='])
  except getopt.error as opterr:
    logger.err(opterr)
    logger.err('for help use --help')
    sys.exit(2)
  # process config and options
  top_number = config.top_number #TODO: remove possibly
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
      if top_number <= 0:
        logger.err('invalid top number: %s' % top_number)
        sys.exit(2)
  # create formatter and parser
  try:
    dbfile = os.path.join(basedir, config.dbfile)
    db = database.Database(dbfile)
    with db:
      display_gui(db, top_number)
  except sqlite3.Error as e:
    logger.err('database error: %s' % e)

def display_gui(db, listsize):
  ui = gui.FreqGUI(db, listsize)
  ui.show()

if __name__ == '__main__':
  main()
