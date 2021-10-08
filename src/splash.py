#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '../images'))


class Splash(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Slimbook Battery")
        # self.set_skip_taskbar_hint(True) # Evita que se muestre icono en taskbar
        main_grid = Gtk.Grid(row_spacing=10,
                             column_homogeneous=True,
                             row_homogeneous=True)
        self.add(main_grid)
        self.set_name('splash_dialog')

        pix_buffer = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'normal.png'),
            width=825,
            height=225,
            preserve_aspect_ratio=True)

        self.set_default_icon(pix_buffer)

        # Set window transparent
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        # set content for the spash window
        pix_buffer = GdkPixbuf.Pixbuf.new_from_file(filename=os.path.join(IMAGES_PATH, 'slimbook_splash.png'))
        logo = Gtk.Image.new_from_pixbuf(pix_buffer)

        pix_buffer_animation = GdkPixbuf.PixbufAnimation.new_from_file(os.path.join(IMAGES_PATH, "splash.gif"))
        image = Gtk.Image()
        image.set_from_animation(pix_buffer_animation)
        image.set_size_request(10, 10)
        image.show()

        main_grid.attach(image, 4, 7, 2, 2)
        main_grid.attach(logo, 0, 0, 10, 11)


def splash_window():
    window = Splash()
    window.connect("destroy", Gtk.main_quit)
    window.set_decorated(False)
    window.set_resizable(False)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()


if __name__ == '__main__':
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path(os.path.join(CURRENT_PATH, 'css/style.css'))

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    splash_window()
    Gtk.main()
