#!/usr/bin/env python3
import gi
import os
from time import sleep
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GdkPixbuf

currpath = os.path.dirname(os.path.realpath(__file__))
imagespath = os.path.normpath(os.path.join(currpath, '..', 'images'))

class Splash(Gtk.Window):
    print('Window object')
    def __init__(self):
        Gtk.Window.__init__(self, title="Slimbook Battery")
        #self.set_skip_taskbar_hint(True) # Evita que se muestre icono en taskbar
        maingrid = Gtk.Grid(row_spacing = 10)
        self.add(maingrid)
        self.set_name('splash_dialog')
        
        # Set window transparent
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        # El gif es de prueba, no el definitivo
        pixbufanim = GdkPixbuf.PixbufAnimation.new_from_file(imagespath+"/slimb3.gif")
        image = Gtk.Image()
        image.set_from_animation(pixbufanim)
        image.show()

        # set content for the spash window
        # pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        #     filename = os.path.join(imagespath, 'normal.png'),
        #     width = 100,
        #     height = 100,
        #     preserve_aspect_ratio=True)
        # logo = Gtk.Image.new_from_pixbuf(pixbuf)

        # label = Gtk.Label("")
        # label.modify_font(Pango.FontDescription('Ubuntu 22'))

        # maingrid.attach(label, 0, 1, 1, 1)
        # maingrid.attach(logo, 0, 0, 1, 1)
        maingrid.attach(image, 0, 0, 1, 1)



def splashwindow():
    print('Window creation')
    window = Splash()
    window.connect("destroy", Gtk.main_quit)
    window.set_decorated(False)
    window.set_resizable(False)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()
        

style_provider = Gtk.CssProvider()
style_provider.load_from_path(currpath+'/css/style.css')

Gtk.StyleContext.add_provider_for_screen (
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
splashwindow()
Gtk.main()