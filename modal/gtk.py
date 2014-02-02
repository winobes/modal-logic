import structure
import pickle
import draw 
import sys
import os

from gi.repository import Gtk
from gi.repository import Pango
from uuid import uuid4

class UiModel(structure.Model):

    def __init__(self, model, name = None, uuid = None):
        super().__init__(model.W, model.R, model.V)        
        self.name = 'Model'
        if not name == None:
            self.name = name
        self.uuid = str(uuid4())
        if not uuid == None:
            self.uuid = uuid

class ModalLogicWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Modal Logic",
                            application=app)
        self.set_default_size(1200, 600)
        self.set_border_width(10)


        if os.path.isfile('modal_data.dat'):
            f = open('modal_data.dat', 'rb')
            self.models = pickle.load(f)
        else:
            self.models = []

        self.current_model = None

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.image = Gtk.Image.new()
    
        self.create_model_view()
        self.create_top_toolbar()
        self.create_draw_window()
        self.create_list_toolbar()

    def create_draw_window(self):

        scroll_window = Gtk.ScrolledWindow()
        self.grid.attach(scroll_window, 1, 1, 1, 1)
        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)
        scroll_window.add(self.image)


    def create_model_view(self):

        scroll_window = Gtk.ScrolledWindow()
        modellist = Gtk.ListStore(str, int, str) 
        view = Gtk.TreeView(model=modellist)
        self.grid.attach(scroll_window, 0, 0, 1, 2)
        scroll_window.add(view)

        view.set_vexpand(True)
        scroll_window.set_min_content_width(250)

        columns = ['Model', 'Size', 'UUID']

        for M in self.models:
            modellist.append([M.name, len(M.W), M.uuid])

        for i in range(len(columns)):
            cell = Gtk.CellRendererText()
            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            col = Gtk.TreeViewColumn(columns[i], cell, text = i)
            view.append_column(col)
       
        view.get_selection().connect('changed', self.model_list_selection_changed) 
   
    def create_top_toolbar(self):

        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 1, 0, 1, 1)

        toolbar.set_hexpand(True)
        toolbar.set_style(1)

        button_add_world = Gtk.ToolButton.new(None, 'Edit Worlds')
        toolbar.insert(button_add_world, 0)
        # needs callback

        button_add_relation = Gtk.ToolButton.new(None, 'Edit Relation')
        toolbar.insert(button_add_relation, 1)
        # needs callback

        button_remove_relation = Gtk.ToolButton.new(None, 'Edit Valuation')
        toolbar.insert(button_remove_relation, 2)
        # needs callback

        toolbar.insert(Gtk.SeparatorToolItem(), 3)

        button_save_models = Gtk.ToolButton.new_from_stock(Gtk.STOCK_SAVE)
        button_save_models.set_label('Save  Model')
        toolbar.insert(button_save_models, 4)
        button_save_models.connect("clicked", self.do_save_models)

        toolbar.insert(Gtk.SeparatorToolItem(), 5)

        button_refresh_drawing = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REFRESH)
        button_refresh_drawing.set_label('(Re)draw Model')
        button_refresh_drawing.connect("clicked", self.draw_to_screen)
        toolbar.insert(button_refresh_drawing, 6)


    def create_list_toolbar(self):

        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 2, 1, 1)



        button_add_model = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
        button_add_model.set_label('Add Model')
        toolbar.insert(button_add_model, 0)
        # needs callback

        button_remove_model = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
        button_remove_model.set_label('Remove Model')
        toolbar.insert(button_remove_model, 1)
        # needs callback
  

    def do_save_models(self, widget):
        f = open("modal_data.dat", 'wb')
        pickle.dump(self.models, f)

    def model_list_selection_changed(self, selection):
        listmodel, treeiter = selection.get_selected()
        if treeiter != None:
            for model in self.models:
                if model.uuid == listmodel[treeiter][2]:
                    self.current_model = model
                    break
        if os.path.isfile(self.current_model.uuid + '.png'):
            print("drawing existig image")
            self.image.set_from_file(self.current_model.uuid + '.png')
        else:
            print("clearing Image")
            self.image.clear()

    def draw_to_screen(self, widget = None):
        M = self.current_model
        if not M == None:
            draw.draw_model(M, M.uuid + '.png')
            self.image.set_from_file(M.uuid + '.png')

class Modal_Logic_Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = ModalLogicWindow(self) 
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = Modal_Logic_Application()
exit_status = app.run(sys.argv)
sys.exit(exit_status)

