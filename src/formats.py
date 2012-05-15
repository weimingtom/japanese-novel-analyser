# -*- coding: utf-8 -*-
"""
formats.py: This file contains formatter for converting specially
formatted files into plain texts.
"""

import os.path
import csv
import re

import config
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
    gaijifile = os.path.join(basedir, config.gaijifile)
    try:
      fp = open(gaijifile, 'r')
    except IOError as e:
      logger.err('error opening gaiji codes file: %s' % (filename, e))
    else:
      with fp:
        for line in fp:
          match = re.match(ur'^0x(?P<JisCode>[0-9A-Fa-f]+)\tU\+(?P<UtfCode>[0-9a-fA-F]+)\+?(?P<UtfCode2>[0-9a-fA-F]+)?', line)
          if match:
            gaiji_code = int(match.group('JisCode'), 16)
            utf_char = unichr(int(match.group('UtfCode'), 16))
            if match.group('UtfCode2'): # 2-character representation
              utf_char = utf_char + unichr(int(match.group('UtfCode2'), 16))
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
    # look for postscript
    if re.match (ur'\s*(底本|このテキストは|本書は|初出)', line):
      self.skip = True
    # if in skip mode, ignore line
    if self.skip:
      return u''
    # replace gaiji
    #line = re.sub(ur'※?［＃.*?(?P<GaijiCode>\d\-\d{1,2}\-\d{1,2})］', self.replace_gaiji, line)
    line = re.sub(ur'※?［＃.*?(?P<JisPlane>\d)\-(?P<JisRow>\d{1,2})\-(?P<JisCol>\d{1,2})］', self.replace_gaiji, line)
    # handle the alteration mark
    line = re.sub(ur'※［＃歌記号］', u'〽', line);
    # remove other Aozora constructs
    line = re.sub(ur'［＃.*?］', u'', line);
    # remove HTML
    line = re.sub(ur'<.*?>', u'', line);
    # remove furigana
    line = re.sub(ur'《.*?》', u'', line);
    line = re.sub(ur'｜', u'', line);
    # remove whitespace
    line = line.strip()
    return line

  def replace_gaiji(self, gaiji_match):
    jis_plane = int(gaiji_match.group('JisPlane'))
    jis_row = int(gaiji_match.group('JisRow'))
    jis_col = int(gaiji_match.group('JisCol'))
    gaiji_code = 0x100 * (jis_row + 0x20) + (jis_col + 0x20)
    if jis_plane == 2:
      gaiji_code = gaiji_code + 0x8080
    try:
      return self.gaiji_codes[gaiji_code]
    except KeyError:
      logger.err('found gaiji with no equivalent: %s' % gaiji_match.group(0))
      return u''

