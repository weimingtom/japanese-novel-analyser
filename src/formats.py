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
This is the base formatter. In itself it just takes texts in plain format
and returns exactly the same text.
"""
class Format(object):
  def __init__(self):
    self.linecount = 0

  def new_file(self):
    self.linecount = 0

  def trim(self, line):
    self.linecount = self.linecount + 1
    return line

"""
This formatter takes texts in the Aozora Bunko format and
strips and/or converts special Aozora constructs to gain plain text.
Gaiji constructs are replaced with UTF-8 equivalents and
other formatting constructs are deleted.
"""
class AozoraFormat(Format):
  def __init__(self, basedir):
    super(AozoraFormat, self).__init__()
    self.skip = False
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
          match = re.match(ur'^(?P<GaijiCode>\d-\d{1,2}-\d{1,2})\t\\UTF{(?P<UtfCode>[0-9a-fA-F]+)}', line)
          if match: # if no match, it is a CID code
            gaiji_code = match.group('GaijiCode')
            utf_char = unichr(int(match.group('UtfCode'), 16))
            self.gaiji_codes[gaiji_code] = utf_char

  def new_file(self):
    Format.new_file(self)
    self.skip = False

  def trim(self, line):
    Format.trim(self, line)
    # look for comment in first 30 lines
    if re.match (ur'----------', line):
      if self.skip:
        self.skip = False
        return u''
      elif self.linecount <= 30:
        self.skip = True
    # look for final words
    if re.match (ur'\s*底本', line) or re.match(ur'\s*このテキストは'):
      self.skip = True
    # if in skip mode, ignore line
    if self.skip:
      return u''
    # replace gaiji
    line = re.sub(ur'※?［＃.*?(?P<GaijiCode>\d\-\d{1,2}\-\d{1,2})］', self.replace_gaiji, line)
    # handle the alteration mark
    line = re.sub(ur'※［＃歌記号］', u'〽', line);
    # remove other Aozora constructs
    line = re.sub(ur'［＃.*?］', u'', line);
    # remove HTML
    line = re.sub(ur'<.*?>', u'', line);
    # remove furigana
    line = re.sub(ur'《.*?》', u'', line);
    line = re.sub(ur'｜', u'', line);
    return line

  def replace_gaiji(self, gaiji_match):
    gaiji_code = gaiji_match.group('GaijiCode')
    try:
      return self.gaiji_codes[gaiji_code]
    except KeyError:
      logger.err('found gaiji with no equivalent: %s' % gaiji_match.group(0))
      return ''

"""
This formatter takes texts with HTML tags and removes them.
"""
class HtmlFormat(Format):
  def __init__(self, basedir):
    super(HtmlFormat, self).__init__()

  def trim(self, line):
    Format.trim(self, line)
    # remove tags
    line = re.sub(ur'<.*?>', u'', line);
    # remove furigana
    line = re.sub(ur'（.*?）', u'', line);
    return line

