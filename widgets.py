from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import sp, dp
from kivy.properties import ObjectProperty, ColorProperty, NumericProperty, ListProperty, StringProperty
# from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.behaviors import MagicBehavior, RectangularRippleBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition
# from kivymd.uix.list import MDList, IRightBodyTouch
from kivymd.uix.segmentedbutton import MDSegmentedButtonItem, MDSegmentedButton
# from kivymd.uix.selection import MDSelectionList
# from kivymd.uix.selection.selection import SelectionItem, SelectionIconCheck
# from kivymd.uix.tab import MDTabsBase
from kivymd.app import MDApp
from kivymd.uix.segmentedbutton.segmentedbutton import MDSegmentedButtonContainer
from kivymd.uix.tooltip import MDTooltip

# class MyImage(AsyncImage):
#     img_id = NumericProperty()
#     index = NumericProperty()
#
#     def on_touch_down(self, touch):
#         if self.disabled and self.collide_point(*touch.pos):
#             with self.canvas:
#                 Color(.5, .8, .2, 1)
#                 setattr(self, 'rad', dp(32))
#                 Ellipse(pos=(touch.x - self.rad/2, touch.y - self.rad/2), size=(self.rad, self.rad))
#                 touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.rad/2)
#             return True
#         for child in self.children[:]:
#             if child.dispatch('on_touch_down', touch):
#                 return True
#
#     def on_touch_move(self, touch):
#         if self.disabled and self.collide_point(*touch.pos):
#             if touch.ud.get('line'):
#                 touch.ud['line'].points += (touch.x, touch.y)
#             return True
#         for child in self.children[:]:
#             if child.dispatch('on_touch_move', touch):
#                 return True
#
#     def on_touch_up(self, touch):
#         if not self.disabled and self.collide_point(*touch.pos):
#             if isinstance(self.parent.parent, MySelectionList) and self.parent.parent.get_selected():
#                 pass
#             else:
#                 return self.open_img_screen()
#         for child in self.children[:]:
#             if child.dispatch('on_touch_up', touch):
#                 return True
#
#     def collide_point(self, x, y):
#         if self.size != self.norm_image_size:
#             width, height = self.norm_image_size
#             left = self.x + (self.width - width) / 2
#             right = self.right - (self.right - (left + width))
#             return left <= x <= right and self.y <= y <= self.top
#         return super(MyImage, self).collide_point(x, y)
#
#     def open_img_screen(self):
#         app = MDApp.get_running_app()
#         screen = app.root.get_screen('open_img_screen')
#         screen.back_screen = app.root.current
#         app.root.transition = RiseInTransition()
#         app.root.current = 'open_img_screen'
#         screen.ids.carousel.index = self.index
#         screen.ids.app_bar.title = 'x'.join(str(self.texture_size).split(', '))
#
#     def get_mask_image(self):
#         change_texture = self.texture.create(size=self.norm_image_size, colorfmt='rgba')
#
#         # Get the pixel data from the texture
#         pixels = bytearray(change_texture.pixels)
#
#         # Modify the pixel data to set every pixel to red
#         for i in range(0, len(pixels), 4):
#             pixels[i] = 255  # red channel
#             pixels[i + 1] = 0  # green channel
#             pixels[i + 2] = 0  # blue channel
#             pixels[i + 3] = 255  # alpha channel
#
#         # Write the modified pixel data back to the texture
#         change_texture.blit_buffer(pixels, colorfmt='rgba')
#
#         self.texture = change_texture
#
#         transparent_texture = self.texture.create(colorfmt='rgba')
#         transparent_texture.mag_filter = 'linear'
#         transparent_texture.min_filter = 'linear_mipmap_linear'
#
#         cords = []
#
#         width, height = self.norm_image_size
#         left = self.x + (self.width - width) / 2
#
#         for elem in self.canvas.children:
#             if isinstance(elem, Line):
#                 for point in elem.points:
#                     if len(cords) < 1:
#                         cords.append([point - left - self.rad/2])
#                     else:
#                         if len(cords[-1]) < 2:
#                             cords[-1].append(point - self.y - self.rad/2)
#                         else:
#                             cords.append([point - left - self.rad/2])
#
#         # Cut out the part of the texture
#         for cord in cords:
#             self.texture.blit_buffer(transparent_texture.pixels, size=(self.rad, self.rad), pos=cord, colorfmt='rgba', bufferfmt='ubyte')
#
#         mask_img = CoreImage(self.texture)
#
#         return mask_img
#
#     def clear_selection(self):
#         if self.disabled:
#             for el in self.canvas.children:
#                 if isinstance(el, Ellipse) or isinstance(el, Line):
#                     self.canvas.children.remove(el)
#


class MySegmentedButton(MDSegmentedButton):
    def __init__(self, **kwargs):
        super(MySegmentedButton, self).__init__(**kwargs)
        self.theme_bg_color = 'Custom'
        self.md_bg_color = 'red'
        self.line_color = 'red'
        print(self.radius)

    def adjust_segment_radius(self, *args) -> None:
        """Rounds off the first and last elements."""

        if self.ids.container.children[0].radius == [0, 0, 0, 0]:
            self.ids.container.children[0].radius = (
                0,
                self.height / 2,
                0,
                0,
            )
        if self.ids.container.children[-1].radius == [0, 0, 0, 0]:
            self.ids.container.children[-1].radius = (
                self.height / 2,
                0,
                0,
                0,
            )

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, MDSegmentedButtonItem):
            widget._segmented_button = self
            widget.bind(on_release=self.mark_item)
            self.ids.container.add_widget(widget)
            # Clock.schedule_once(self.adjust_segment_radius)
        elif isinstance(widget, MDSegmentedButtonContainer):
            return super(MySegmentedButton, self).add_widget(widget)


# class MySelectionList(MDSelectionList):
#     screen = ObjectProperty()
#     toolbar = ObjectProperty()
#     progress_round_color = ColorProperty('#ed1c1c')
#     back_item = ListProperty(['arrow-left-bold'])
#
#     def add_widget(self, widget, index=0, canvas=None):
#
#         selection_icon = SelectionIconCheck(
#             icon=self.icon,
#             size_hint=(.2, .2),
#             pos_hint={'center_x': .15, 'center_y': .85},
#             md_bg_color=self.icon_bg_color,
#             icon_check_color=self.icon_check_color,
#         )
#
#         selection_item = SelectionItem(
#             size_hint=(1, 1),
#             height=widget.height,
#             instance_item=widget,
#             instance_icon=selection_icon,
#             overlay_color=self.overlay_color,
#             progress_round_size=self.progress_round_size,
#             progress_round_color=self.progress_round_color,
#             owner=self,
#         )
#
#         selection_item.add_widget(widget)
#         selection_item.add_widget(selection_icon)
#
#         return super(MDList, self).add_widget(selection_item, index, canvas)
#
#     def set_selection_mode(self, instance_selection_list, mode):
#         if mode:
#             self.toolbar.left_action_items.remove(self.toolbar.left_action_items[0])
#             self.toolbar.left_action_items.append(["close-thick", lambda x: self.unselected_all()])
#             self.toolbar.right_action_items.insert(0, ['delete', lambda x: self.screen.delete_images(widget_list=instance_selection_list.get_selected_list_items())])
#         else:
#             self.toolbar.left_action_items.remove(self.toolbar.left_action_items[0])
#             self.toolbar.left_action_items.append(self.back_item)
#             self.toolbar.right_action_items.remove(self.toolbar.right_action_items[0])
#             self.toolbar.title = ""
#
#     def selected(self, instance_selection_list, instance_selection_item):
#         self.toolbar.title = str(len(instance_selection_list.get_selected_list_items()))
#
#     def unselected(self, instance_selection_list, instance_selection_item):
#         if instance_selection_list.get_selected_list_items():
#             self.toolbar.title = str(len(instance_selection_list.get_selected_list_items()))
#
#
# class RightLabel(IRightBodyTouch, MDLabel):
#     pass
#
#
# # class Tab(MDFloatLayout, MDTabsBase):
# #     '''Class implementing content for a tab.'''
# #
#
# class MyIconButton(MagicBehavior, MDIconButton):
#
#     def __init__(self, **kwargs):
#         super(MyIconButton, self).__init__(**kwargs)
#         self.ripple_effect = False
#
#     def on_release(self):
#         self.grow()


# class ActionTopAppBarButton(MyIconButton, MDTooltip):
#     overflow_text = StringProperty()


# class MyTopAppBar(MDTopAppBar):
#
#     def __init__(self, **kwargs):
#         super(MyTopAppBar, self).__init__(**kwargs)
#
#     def update_action_bar(
#             self, instance_box_layout, action_bar_items: list
#     ) -> None:
#         instance_box_layout.clear_widgets()
#         new_width = 0
#
#         for item in action_bar_items:
#             new_width += dp(48)
#             if len(item) == 1:
#                 item.append(lambda x: None)
#             if len(item) > 1 and not item[1]:
#                 item[1] = lambda x: None
#             if len(item) == 2:
#                 if isinstance(item[1], str) or isinstance(item[1], tuple):
#                     item.insert(1, lambda x: None)
#                 else:
#                     item.append("")
#             if len(item) == 3:
#                 if isinstance(item[2], tuple):
#                     item.insert(2, "")
#
#             instance_box_layout.add_widget(
#                 ActionTopAppBarButton(
#                     icon=item[0],
#                     on_release=item[1],
#                     tooltip_text=item[2],
#                     overflow_text=item[3]
#                     if (len(item) == 4 and isinstance(item[3], str))
#                     else "",
#                     theme_text_color="Custom"
#                     if not self.opposite_colors
#                     else "Primary",
#                     text_color=self.specific_text_color
#                     if not (len(item) == 4 and isinstance(item[3], tuple))
#                     else item[3],
#                     opposite_colors=self.opposite_colors,
#                     md_bg_color=self.md_bg_color,
#                 )
#             )
#
#         instance_box_layout.width = new_width


# class Message(RectangularRippleBehavior, ButtonBehavior, MDRelativeLayout):
#     message = StringProperty()
#     time = StringProperty()
#     image_path = StringProperty()
#     triangle_points = ListProperty()
#
#     def on_release(self):
#         Clipboard.copy(self.message)

