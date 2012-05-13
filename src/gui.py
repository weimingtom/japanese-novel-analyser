# -*- coding: utf-8 -*-

"""
gui.py: This is the graphical user interface.
"""

import gtk

import config

class FreqGUI():
  def __init__(self, disp):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect('delete_event', self.delete_event)
    self.window.connect('destroy', self.destroy)
    self.window.set_border_width(10)
    self.window.set_title('Frequency Browser')
    topbox = gtk.VBox(False, 10)
    hbox = gtk.HBox(True, 10)
    self.store = gtk.ListStore(float, str, *([str]*config.mecab_fields))
    # test
    self.store.append([0.123, '日本', '名詞', '一般', '*', '*', '#', '#'])
    self.store.append([100.123, '日本語能力試験', '名詞', '名前', '組織', '語学', '#', '#'])

    sw = gtk.ScrolledWindow()
    sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    view = gtk.TreeView(self.store)
    self.add_columns(view)
    view.set_rules_hint(True)
    sw.add(view)
    topbox.pack_start(hbox, False, False)
    topbox.pack_start(sw, True, True)
    self.window.add(topbox)
    # create selection vars
    self.posvars = []
    for i in range(config.mecab_fields):
      selvar = 'pos' + str(i)
      self.posvars.append(selvar)
      if i < 4:
        selvar = '*'
      else:
        selvar = 'IGNORE'
    selmax = 0
    ignmin = 4
    vbox = gtk.VBox(False, 0)
    lb = gtk.Label('Search')
    entry = gtk.Entry(max=10)
    entry.connect('activate', self.changed_word)
    entry.set_width_chars(5)
    vbox.pack_start(lb, False, False, 0)
    vbox.pack_start(entry, False, False, 0)
    hbox.pack_start(vbox, True, True, 0)

    vbox = gtk.VBox(False, 0)
    lb = gtk.Label('Word')
    entry = gtk.Entry(max=40)
    entry.connect('activate', self.changed_word)
    entry.set_width_chars(10)
    vbox.pack_start(lb, False, False, 0)
    vbox.pack_start(entry, False, False, 0)
    hbox.pack_start(vbox, True, True, 0)
    for i in range(config.mecab_fields):
      vbox = gtk.VBox(False, 0)
      cb = gtk.combo_box_new_text()
      options = []
      options.append('*')
      if i <= selmax:
        cb.append_text('*')
      if i >= ignmin:
        cb.append_text('IGNORE')
      if self.posvars[i] == 'IGNORE':
        ignmin = i
      elif self.posvars[i] != '*':
        selmax = i + 1
      cb.set_active(0)
      cb.connect('changed', self.changed_pos, i)
      lb = gtk.Label(' ' + str(i + 1))
      vbox.pack_start(lb, False, False, 0)
      vbox.pack_start(cb, False, False, 0)
      hbox.pack_start(vbox, True, True, 0)
    self.window.show_all()

  def add_columns(self, view):
    rt = gtk.CellRendererText()
    column = gtk.TreeViewColumn('Freq', rt, text=0)
    column.set_expand(True)
    view.append_column(column)

    rt = gtk.CellRendererText()
    column = gtk.TreeViewColumn('Word', rt, text=1)
    column.set_expand(True)
    view.append_column(column)
    
    for i in range(config.mecab_fields):
      rt = gtk.CellRendererText()
      column = gtk.TreeViewColumn('POS' + str(i + 1), rt, text=(i + 2))
      column.set_expand(True)
      view.append_column(column)
  
  def delete_event(self, widget, event, data=None):
    # allow window to be destroyed by delete event
    return False

  def destroy(self, widget, data=None):
    gtk.main_quit()

  def changed_word(self, entry):
    text = entry.get_text()
    print('changed word to %s' % (text))

  def changed_pos(self, combobox, number):
    model = combobox.get_model()
    index = combobox.get_active()
    print('changed %s to %s' % (number, model[index][0]))

  def show(self):
    gtk.main()


