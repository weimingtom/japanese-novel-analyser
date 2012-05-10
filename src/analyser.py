#!/usr/bin/env python2

"""
This is the Japanese Novel Analyser.
It reads in novels from files in aozora formatting, strips this formatting,
invokes the mecab morphological analysis and counts word frequencies.

Usage: analyser.py [OPTION]... FILE..
Read and analyse each FILE.

Options:
  -h, --help          Display this help
  -e, --encoding=ENC  Set the encoding for the files to ENC
  -f, --format=FORMAT Set the format of the files;
                      FORMAT is `aozora' or `plain`
"""

import sys
import getopt
import codecs
import os.path
import MeCab

import formats
from logger import logger

def main():
  # get path of main program directory
  basedir =  os.path.normpath(os.path.join(
      os.path.split(sys.argv[0])[0], os.pardir))
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hf:e:', ['help','format=','encoding='])
  except getopt.error as opterr:
    logger.err(opterr)
    logger.err('for help use --help')
    sys.exit(2)
  # process options
  mode = 'analyse'#TODO: make switchable
  formatter = 'aozora'
  encoding = 'utf-8'
  for o, a in opts:
    if o in ('-h', '--help'):
      logger.out(__doc__)
      sys.exit(0)
    if o in ('-f', '--format'):
      formatter = a
      if formatter not in ('plain', 'aozora'):
        logger.err('format not supported: %s' % formatter)
        sys.exit(2)
    if o in ('-e', '--encoding'):
      encoding = a
      try:
        codecs.lookup(encoding)
      except LookupError:
        logger.err('encoding not found: %s' % encoding)
        sys.exit(2)
  # create formatter
  if(formatter == 'aozora'):
    formatter = formats.AozoraFormat(basedir)
  else:
    formatter = formats.PlainFormat()
  # check mode
  if mode == 'analyse':
    # process files
      logger.out('analyzing text files')
      analyze(args, formatter, encoding)
      logger.out('done analyzing')
  else:
    logger.out('no mode given, exiting')

def analyze(files, formatter, encoding):
  # process all files line by line
  for filename in files:
    logger.out('reading %s' % filename)
    try:
      fp = codecs.open(filename, 'r', encoding)
    except IOError as e:
      logger.err('error opening %s: %s' % (filename, e))
    else:
      with fp:
        for line in fp:
          sline = formatter.trim(line)
          sys.stdout.write(sline)
          #TODO: continue analysing with Mecab 

if __name__ == '__main__':
  main()
