# -*- coding: utf-8 -*-

"""
gui.py: This is the graphical user interface.
"""

import gtk

import config

class FreqGUI():
  def __init__(self, db):
    self.database = db
    self.freqmode = 0
    self.word = u''
    self.posvalues = [config.ALL]*config.mecab_fields
    self.update_mode = False
    self.create_layout()
    self.update()
    self.window.show_all()

  def create_layout(self):
    # main window
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect('delete_event', self.delete_event)
    self.window.connect('destroy', self.destroy)
    self.window.set_default_size(800, 600)
    self.window.set_title('Frequency Browser')
    self.window.set_border_width(5)
    # words displayed in scrollable list view
    sw = gtk.ScrolledWindow()
    sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.store = gtk.ListStore(float, str, *([str]*config.mecab_fields))
    self.view = gtk.TreeView(self.store)
    self.add_columns(self.view)
    self.view.set_rules_hint(True)
    sw.add(self.view)
    # split with selection boxes, word list and status bar
    topbox = gtk.VBox(False, 10)
    hbox = gtk.HBox(True, 10)
    self.status = gtk.Label('')
    topbox.pack_start(hbox, False, False)
    topbox.pack_start(sw, True, True)
    topbox.pack_start(self.status, False, False)
    self.window.add(topbox)
    # create selection vars
    # frequency display selection box
    vbox = gtk.VBox(False, 0)
    lb = gtk.Label('Frequency')
    cb = gtk.combo_box_new_text()
    cb.append_text('Relative')
    cb.append_text('Absolute')
    cb.set_active(0)
    cb.set_size_request(50, -1)
    cb.connect('changed', self.changed_freq)
    vbox.pack_start(lb, False, False, 0)
    vbox.pack_start(cb, False, False, 0)
    hbox.pack_start(vbox, True, True, 0)
    # word selection box
    vbox = gtk.VBox(False, 0)
    lb = gtk.Label('Word')
    entry = gtk.Entry(max=40)
    entry.connect('activate', self.changed_word)
    entry.set_width_chars(5)
    vbox.pack_start(lb, False, False, 0)
    vbox.pack_start(entry, False, False, 0)
    hbox.pack_start(vbox, True, True, 0)
    # pos selection boxes
    self.pos_boxes = []
    self.pos_stores = []
    for i in range(config.mecab_fields):
      vbox = gtk.VBox(False, 0)
      store = gtk.ListStore(str)
      cell = gtk.CellRendererText()
      cb = gtk.ComboBox(store)
      cb.pack_start(cell, True)
      cb.add_attribute(cell, 'text', 0)
      cb.set_size_request(50, -1)
      cb.connect('changed', self.changed_pos, i)
      lb = gtk.Label('POS ' + str(i + 1))
      vbox.pack_start(lb, False, False, 0)
      vbox.pack_start(cb, False, False, 0)
      hbox.pack_start(vbox, True, True, 0)
      self.pos_boxes.append(cb)
      self.pos_stores.append(store)

  def update_selections(self):
    self.update_mode = True
    # get valid selections
    all_options = self.database.select_options(self.word, self.posvalues)
    for i in range(config.mecab_fields):
      cb = self.pos_boxes[i]
      store = self.pos_stores[i]
      cb.hide()
      store.clear()
      options = all_options[i]
      for j in range(len(options)):
        opt = options[j]
        store.append((options[j],))
        if options[j] == self.posvalues[i]:
          cb.set_active(j)
      cb.show()
    self.update_mode = False

  def update_list(self):
    (results, fsum) = self.database.select(self.word, self.posvalues, 50)
    self.view.hide()
    self.store.clear()
    for r in results:
      rl = list(r)
      if not self.freqmode:
        rl[0] = 100.00 * rl[0] / fsum
      self.store.append(rl)
    self.view.show()

  """ add header columns to view """
  def add_columns(self, view):
    rt = gtk.CellRendererText()
    self.freqcolumn = gtk.TreeViewColumn('Frequency (%)', rt, text=0)
    self.freqcolumn.set_expand(True)
    view.append_column(self.freqcolumn)

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

  def update(self):
    if not self.update_mode: # to prevent recursive updates
      self.update_list()
      self.update_selections()

  def changed_word(self, entry):
    self.word = entry.get_text().decode('utf-8')
    self.update()

  def changed_freq(self, freqbox):
    index = freqbox.get_active()
    self.freqmode = freqbox.get_active()
    if self.freqmode:
      self.freqcolumn.set_title('Frequency (#)')
    else:
      self.freqcolumn.set_title('Frequency (%)')
    self.update()

  def changed_pos(self, combobox, number):
    if not self.update_mode:
      index = combobox.get_active()
      self.posvalues[number] = self.pos_stores[number][index][0].decode('utf-8')
      self.update()

  def list_scroll(self, view):
    pass

  def show(self):
    gtk.main()


