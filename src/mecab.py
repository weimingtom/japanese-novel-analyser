# -*- coding: utf-8 -*-
"""
mecab.py: This file invokes the Mecab morphological analyser on the
cleaned input files and parses its output for further processing.
"""

import sys
import re
import MeCab

import config
from logger import logger

class PyMeCab():
  def __init__(self):
    self.tagger = MeCab.Tagger('')
    self.fields = config.mecab_fields

  def parse(self, line):
    node = self.tagger.parseToNode(line.encode('utf-8'))
    data = []
    while node:
      if node.stat == 0 or node.stat == 1: # MECAB_NOR_NODE or MECAB_UNK_NODE
        try:
          word = node.surface.decode('utf-8')
          fields = node.feature.decode('utf-8').split(',')
          # get part-of-speech features 
          #print('node %s with type %s and len %s' % (word, type(word), len(word)))
          pos = fields[0:self.fields]
          if len(fields) > 6 and fields[6] != '*': # take root
            word = fields[6] 
          fieldvalues = [word] + pos
          data.append(fieldvalues)
        except UnicodeDecodeError as e:
          logger.err('could not decode %s' % node.surface)
      # else MECAB_BOS_NODE or MECAB_EOS_NOD, ignore
      node = node.next
    return data

