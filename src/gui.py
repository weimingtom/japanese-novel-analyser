# -*- coding: utf-8 -*-

"""
gui.py: This is the graphical user interface.
"""

import gtk

import config

class FreqGUI():
  def __init__(self, db, listsize):
    self.database = db
    self.listsize = listsize
    self.freqmode = 0
    self.word = u''
    self.posvalues = [config.ALL]*config.mecab_fields
    self.update_mode = False
    self.storeend = None
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
    self.view.connect('row-activated', self.list_select)
    sw.add(self.view)
    # split with selection boxes, word list and status bar
    topbox = gtk.VBox(False, 10)
    hbox = gtk.HBox(True, 10)
    self.status = gtk.Statusbar()
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
    self.dsum = 0
    self.fsum = self.database.select(self.word, self.posvalues)
    self.view.hide()
    self.store.clear()
    self.load_list()
    self.view.show()

  def load_list(self):
    results = self.database.select_results(self.listsize)
    print('loading %s more' % len(results))
    self.view.hide()
    for r in results:
      rl = list(r)
      self.dsum = self.dsum + r[0] 
      if not self.freqmode:
        rl[0] = 100.00 * rl[0] / self.fsum
      self.store.append(rl)
    if len(results) >= self.listsize:
      remaining = self.fsum - self.dsum
      if not self.freqmode:
        remaining = 100.00 * remaining / self.fsum
      self.storeend = self.store.append([remaining, u'Load more…'] + [u'']*config.mecab_fields)
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
      # important to first update selections so db cursor
      # for the list is preserved
      self.update_selections()
      self.update_list()

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

  def list_select(self, view, row, col):
    print('selected %s, %s' % (row, col))
    text = self.store[row][1].decode('utf-8')
    self.status.push(0, self.store[row][1])
    #print('scrolled to %s, %s' % (hadjustment.get_value(), vadjustment.get_value()))
    if self.storeend != None and self.store.get_value(self.storeend, 1) == text:
      self.store.remove(self.storeend)
      self.storeend = None
      self.load_list()

  def show(self):
    gtk.main()


