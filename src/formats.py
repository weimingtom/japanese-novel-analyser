# -*- coding: utf-8 -*-
"""
formats.py: This file contains formatter for converting specially
formatted files into plain texts.
"""

import os.path
import csv
import re

from logger import logger

"""
This formatter takes texts in plain format and returns exactly the
same text.
"""
class PlainFormat:
  def trim(self, string):
    return string

"""
This formatter takes texts in the Aozora Bunko format and
strips and/or converts special Aozora constructs to gain plain text.
Gaiji constructs are replaced with UTF-8 equivalents and
other formatting constructs are deleted.
"""
class AozoraFormat:
  def __init__(self, basedir):
    # load gaiji codes
    self.gaiji_codes = {}
    gaiji_file = os.path.join(basedir, 'data/gaiji_codes')
    try:
      fp = open(gaiji_file, 'r')
    except IOError as e:
      logger.err('error opening gaiji codes file: %s' % (filename, e))
    else:
      with fp:
        for line in fp:
          match = re.match(r'^(?P<GaijiCode>\d-\d{1,2}-\d{1,2})\t\\UTF{(?P<UtfCode>[0-9a-fA-F]+)}', line)
          if match: # if no match, it is a CID code
            gaiji_code = match.group('GaijiCode')
            utf_char = unichr(int(match.group('UtfCode'), 16))
            self.gaiji_codes[gaiji_code] = utf_char

  def trim(self, string):
    string = unicode(string)
    # replace gaiji
    repl = re.sub(ur'※?［＃.*?(?P<GaijiCode>\d\-\d{1,2}\-\d{1,2})］', self.replace_gaiji, string, flags=re.UNICODE)
    # replace other aozora constructs
    # replace furigana
    return repl

  def replace_gaiji(self, gaiji_match):
    gaiji_code = gaiji_match.group('GaijiCode')
    try:
      return self.gaiji_codes[gaiji_code]
    except KeyError:
      logger.err('found gaiji with no equivalent: %s' % gaiji_match.group(0))
      return ''

