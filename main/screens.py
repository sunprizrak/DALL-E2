from kivy.metrics import sp, dp
from kivy.uix.label import Label
from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from kivy.core.image import Image as CoreImage
from kivymd.uix.transition import MDSwapTransition
from .widgets import MyImage
from .controller import OpenAIController
from main.controller import ImageController
import io
import base64
import uuid
from os.path import join, exists
from PIL import Image as PilImage
from kivy.utils import platform
from users.controller import UserController
import logging

logging.getLogger('PIL').setLevel(logging.WARNING)


class StartScreen(MDScreen):
    core = ObjectProperty()


class SettingsScreen(MDScreen):
    pass


class MainScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def open_settings(self):
        self.ids.nav_drawer.set_state("close")
        self.core.root.transition = MDSwapTransition()
        self.core.root.current = 'settings_screen'

    def open_collection(self):
        screen = self.core.root.current
        self.core.root.ids.collection_screen.ids.selection_list.back_item = ['arrow-left', lambda x: self.core.back(screen=screen)]
        self.ids.nav_drawer.set_state("close")
        self.core.root.transition = MDSwapTransition()
        self.core.root.current = 'collection_screen'

    def exit(self):
        self.ids.nav_drawer.set_state("close")
        self.user_controller.un_login()


class CreateImageScreen(MDScreen):
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    default_img = ObjectProperty()

    def __init__(self, **kwargs):
        super(CreateImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.image_controller = ImageController(screen=self)

    def create(self):

        def callback(request, response):
            self.ids.create_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    allow_stretch=True,
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
            elif len(response['data']) > 1:
                swiper = MDSwiper(
                    size_hint_y=None,
                    pos_hint={'center_x': .5, 'center_y': .5},
                    height=self.ids.image_section.height,
                )

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)
        if all([self.prompt, self.image_count, self.image_size]):
            for widget in self.ids.image_section.children:
                if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                    self.ids.image_section.remove_widget(widget)

            self.ids.image_section.remove_widget(self.default_img)

            self.ids.create_spin.active = True

            self.openai_controller.image_generation(
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                callback=callback,
            )


class EditImageScreen(MDScreen):
    core = ObjectProperty()
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    image_original = io.BytesIO()
    image_mask = io.BytesIO()

    def __init__(self, **kwargs):
        super(EditImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()

    def add_image(self, path):
        self.ids.add_image_button.disabled = True

        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        image = MyImage(
            disabled=True,
            source=path,
            allow_stretch=True,
            mipmap=True,
        )

        self.ids.image_section.add_widget(image)
        self.ids.edit_top_bar.right_action_items.append(["autorenew", lambda x: self.reload_image()])
        self.ids.edit_top_bar.right_action_items.append(["broom", lambda x: self.clear_selection()])

        with PilImage.open(path) as img:
            new = img.resize(size=(256, 256))
            new.save(self.image_original, format='png')

    def edit_image(self):

        def callback(request, response):
            self.ids.edit_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    allow_stretch=True,
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
            elif len(response['data']) > 1:
                swiper = MDSwiper()

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)

        def callback_failure(request, response):
            self.ids.edit_spin.active = False
            self.ids.add_image_button.disabled = False
            print('failure')

        def callback_error(request, error):
            self.ids.edit_spin.active = False
            self.ids.add_image_button.disabled = False
            print('error')

        self.image_original.seek(0)
        if len(self.image_original.getvalue()) > 0:
            if all([self.prompt, self.image_count, self.image_size]):
                for widget in self.ids.image_section.children:
                    if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                        if isinstance(widget, MyImage) and widget.disabled:
                            mask_img = self.ids.image_section.children[0].get_mask_image()
                            mask_data = io.BytesIO()
                            mask_img.save(mask_data, flipped=True, fmt='png')

                            with PilImage.open(mask_data) as img:
                                new = img.resize(size=(256, 256))
                                new.save(self.image_mask, format='png')

                        self.ids.image_section.remove_widget(widget)

                self.ids.add_image_button.disabled = True
                self.ids.edit_spin.active = True

                self.image_original.seek(0)
                png_image_original = self.image_original.getvalue()
                im_b64_image_original = base64.b64encode(png_image_original).decode('utf-8')

                self.image_mask.seek(0)
                png_image_mask = self.image_mask.getvalue()
                im_b64_image_mask = base64.b64encode(png_image_mask).decode('utf-8')

                self.openai_controller.image_edit(
                    image=im_b64_image_original,
                    mask=im_b64_image_mask,
                    prompt=self.prompt,
                    image_count=self.image_count,
                    image_size=self.image_size,
                    callback=callback,
                    on_error=callback_error,
                    on_failure=callback_failure,
                )

    def clear_selection(self):
        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage):
                widget.clear_selection()

    def reload_image(self):
        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        self.image_original.truncate(0)
        self.image_mask.truncate(0)
        self.ids.add_image_button.disabled = False

        while len(self.ids.edit_top_bar.right_action_items) !=0:
            self.ids.edit_top_bar.right_action_items.remove(self.ids.edit_top_bar.right_action_items[-1])


class VariableImageScreen(MDScreen):
    image = io.BytesIO()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')

    def __init__(self, **kwargs):
        super(VariableImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()

    def add_image(self, path):
        self.ids.add_image_button.disabled = True

        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        image = MyImage(
            source=path,
            allow_stretch=True,
            mipmap=True,
        )

        self.ids.image_section.add_widget(image)
        self.ids.variable_top_bar.right_action_items.append(["autorenew", lambda x: self.reload_image()])

        with PilImage.open(path) as img:
            new = img.resize(size=(256, 256))
            new.save(self.image, format='png')

    def reload_image(self):
        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        self.image.truncate(0)
        self.ids.add_image_button.disabled = False

        self.ids.variable_top_bar.right_action_items.remove(self.ids.variable_top_bar.right_action_items[-1])

    def generate(self):

        def callback(request, response):
            self.ids.variable_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    allow_stretch=True,
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
            elif len(response['data']) > 1:
                swiper = MDSwiper()

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)

        def callback_failure(request, response):
            print(response)
            self.ids.variable_spin.active = False
            self.ids.add_image_button.disabled = False

        def callback_error(request, error):
            print(error)
            self.ids.variable_spin.active = False
            self.ids.add_image_button.disabled = False

        self.image.seek(0)
        if len(self.image.getvalue()) > 0:

            if all([self.image_count, self.image_size]):

                for widget in self.ids.image_section.children:
                    if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                        self.ids.image_section.remove_widget(widget)

                self.ids.add_image_button.disabled = True
                self.ids.variable_spin.active = True

                self.image.seek(0)
                image_png = self.image.getvalue()
                im_b64_image = base64.b64encode(image_png).decode('utf-8')

                self.openai_controller.image_variation(
                    image=im_b64_image,
                    image_count=self.image_count,
                    image_size=self.image_size,
                    callback=callback,
                    on_error=callback_error,
                    on_failure=callback_failure,
                )


class ChatGptScreen(MDScreen):
    core = ObjectProperty()
    prompt = StringProperty()

    def __init__(self, **kwargs):
        super(ChatGptScreen, self).__init__(*kwargs)
        self.openai_controller = OpenAIController()

    def send(self):

        def callback(request, response):
            text = response['choices'][0].get('text').lstrip()

            lab = Label(text=text, font_size=sp(16), padding_x=dp(20), padding_y=dp(5))
            lab.texture_update()
            w, h = lab.texture_size

            if w > dp(300):
                lab = Label(text=text, font_size=sp(16), padding_x=dp(20), padding_y=dp(5), text_size=(dp(300), None))
                lab.texture_update()
                w, h = lab.texture_size

            msg = {
                'width': w,
                'height': h,
                'text': text,
                'theme_text_color': 'Custom',
                'text_color': (1, 1, 1, 1),
                'bg_color': (.2, .2, .2, 1),
                'radius': [10, 10, 10, 10],
                'pos_hint': {'left': 1},
            }

            self.ids.chat_gpt.data.append(msg)

        if self.prompt:

            label = Label(text=self.prompt, font_size=sp(16), padding_x=dp(20), padding_y=dp(5))
            label.texture_update()
            width, height = label.texture_size

            if width > dp(300):
                label = Label(text=self.prompt, font_size=sp(16), padding_x=dp(20), padding_y=dp(5), text_size=(dp(300), None))
                label.texture_update()
                width, height = label.texture_size

            message = {
                'width': width,
                'height': height,
                'text': self.prompt,
                'theme_text_color': 'Custom',
                'text_color': (1, 1, 1, 1),
                'bg_color': (.2, .2, .2, 1),
                'radius': [10, 10, 10, 10],
                'pos_hint': {'right': 1},
            }

            self.ids.chat_gpt.data.append(message)

            self.openai_controller.text_completion(
                prompt=self.prompt,
                callback=callback,
            )


class CollectionScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(CollectionScreen, self).__init__(**kwargs)
        self.image_controller = ImageController(screen=self)

        menu_items = [
            {
                'text': 'Choose all',
                'viewclass': 'OneLineListItem',
                'on_release': lambda: (self.ids.selection_list.selected_all(), self.menu.dismiss()),
            }
        ]

        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=2.5,
        )

    def menu_callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def delete_images(self, widget_list):
        images_id = [widget.children[1].img_id for widget in widget_list]

        def del_images():
            self.image_controller.del_images(images_id=images_id, widget_list=widget_list)
            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Delete",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: del_images(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Delete'
        self.core.dialog.text = 'Are you sure you want to delete?'


class OpenImageScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(OpenImageScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)
        self.image_controller = ImageController(screen=self)

    def back(self, screen):
        if len(self.ids.app_bar.right_action_items) > 1:
            self.ids.app_bar.right_action_items.remove(self.ids.app_bar.right_action_items[0])
        self.parent.transition = FallOutTransition()
        self.parent.current = screen

    def download(self, img):

        def save_image():
            image = CoreImage(img.texture)

            if platform == 'android':
                private_path = join(self.core.ss.get_cache_dir(), f'{str(uuid.uuid4())}.png')
                print(img.source)

                image.save(private_path)

                if exists(private_path):
                    self.core.ss.copy_to_shared(private_path)

            if img.back_screen in ('create_image_screen', 'edit_image_screen', 'variable_image_screen'):
                data = io.BytesIO()
                image.save(data, fmt='png')
                png_bytes = data.read()
                im_b64 = base64.b64encode(png_bytes).decode('utf-8')

                data_image = {
                    'user': self.user_controller.user.id,
                    'source': im_b64,
                    'description': self.core.root.ids.create_image_screen.prompt,
                }

                self.image_controller.save_image(data_image=data_image)

            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Save",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: save_image(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Save image'
        self.core.dialog.text = 'Do you want to save the picture?'

    def delete(self, img_id, widget):

        def del_image():
            self.image_controller.del_image(image_id=img_id, widget=widget)
            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Delete",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: del_image(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Delete'
        self.core.dialog.text = 'Are you sure you want to delete??'