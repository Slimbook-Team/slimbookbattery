#!/usr/bin/env python3
import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

currpath = os.path.dirname(os.path.realpath(__file__))
imagespath = os.path.normpath(os.path.join(currpath, '..', 'images'))

class Splash(Gtk.Window):
    print('Window object')
    def __init__(self):
        Gtk.Window.__init__(self, title="Slimbook Battery")
        #self.set_skip_taskbar_hint(True) # Evita que se muestre icono en taskbar
        maingrid = Gtk.Grid(row_spacing = 10,
                            column_homogeneous =True,
                            row_homogeneous =True)
        self.add(maingrid)
        self.set_name('splash_dialog')
        
        # Set window transparent
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)      

        #set content for the spash window
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename = os.path.join(imagespath, 'slimbook_splash.png'))
        """ pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename = os.path.join(imagespath, 'slimbook_splash.png'),
            width = 500,
            height = 500,
            preserve_aspect_ratio=True) """
        logo = Gtk.Image.new_from_pixbuf(pixbuf)

        """ pixbufanim = GdkPixbuf.PixbufAnimation.new_from_file(
                imagespath+"/loading2.gif")
        image = Gtk.Image()
        image.set_from_animation(pixbufanim)
        image.set_size_request(10, 10)
        image.show() """

        #maingrid.attach(image, 4, 7, 2, 2)
        maingrid.attach(logo, 0, 0, 10, 11)
        



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