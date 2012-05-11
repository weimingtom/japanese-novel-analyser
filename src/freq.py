"""
freq.py: This file computes up the frequencies of the words given my
the morphological analyser by aggregating based on the root form and the
part-of-speech.
"""

class FrequencyCounter():
  def __init__(self):
    self.freqs = {}

  def add_word(self, word_data):
    if word_data in self.freqs:
      self.freqs[word_data] = self.freqs[word_data] + 1
    else:
      self.freqs[word_data] =  1

  def display_list(self):
    fsort = sorted(self.freqs, key=self.freqs.get, reverse=True)
    for word_data in fsort:
      pass
      #print(("%s: %s" % (word_data, self.freqs[word_data])).encode('utf-8'))
    wsort = sorted(self.freqs)
    for word_data in wsort:
      pass
      #print(("%s: %s" % (word_data, self.freqs[word_data])).encode('utf-8'))
