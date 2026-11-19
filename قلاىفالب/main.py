import os

os.environ["RAIL_OPERATOR_KIVY"] = "1"

import pygame
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget

from لعبه import HEIGHT, WIDTH, TrainGame


KEY_CODES = {
    "escape": pygame.K_ESCAPE,
    "enter": pygame.K_RETURN,
    "n": pygame.K_n,
    "p": pygame.K_p,
    "w": pygame.K_w,
    "s": pygame.K_s,
    "x": pygame.K_x,
    "c": pygame.K_c,
    "h": pygame.K_h,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "1": pygame.K_1,
    "2": pygame.K_2,
    "3": pygame.K_3,
    "4": pygame.K_4,
    "6": pygame.K_6,
    "7": pygame.K_7,
    "8": pygame.K_8,
}


class TrainView(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.texture = Texture.create(size=(WIDTH, HEIGHT), colorfmt="rgba")
        self.texture.flip_vertical()
        with self.canvas:
            Color(1, 1, 1, 1)
            self.image = Rectangle(texture=self.texture, pos=self.pos, size=self.size)
        self.bind(pos=self._resize_image, size=self._resize_image)

    def _resize_image(self, *_args):
        scale = min(self.width / WIDTH, self.height / HEIGHT)
        image_width = WIDTH * scale
        image_height = HEIGHT * scale
        self.image.size = image_width, image_height
        self.image.pos = (
            self.x + (self.width - image_width) / 2,
            self.y + (self.height - image_height) / 2,
        )

    def render(self, _dt):
        if not self.game.running:
            App.get_running_app().stop()
            return
        self.game.update(min(_dt, 0.05))
        self.game.draw()
        pixels = pygame.image.tostring(self.game.screen, "RGBA")
        self.texture.blit_buffer(pixels, colorfmt="rgba", bufferfmt="ubyte")

    def _game_position(self, touch):
        image_x, image_y = self.image.pos
        image_width, image_height = self.image.size
        x = (touch.x - image_x) * WIDTH / max(1, image_width)
        y_from_bottom = (touch.y - image_y) * HEIGHT / max(1, image_height)
        return int(x), int(HEIGHT - y_from_bottom)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        image_x, image_y = self.image.pos
        image_width, image_height = self.image.size
        if not (image_x <= touch.x <= image_x + image_width
                and image_y <= touch.y <= image_y + image_height):
            return True
        x, y = self._game_position(touch)
        self.game._pointer_down(("kivy", touch.uid), (x, y))
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        self.game._pointer_move(("kivy", touch.uid), self._game_position(touch))
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        self.game._pointer_up(("kivy", touch.uid))
        touch.ungrab(self)
        return True


class RailOperatorApp(App):
    def build(self):
        self.game = TrainGame()
        Window.bind(on_key_down=self._key_down, on_key_up=self._key_up)
        self.view = TrainView(self.game)
        Clock.schedule_interval(self.view.render, 1 / 60)
        return self.view

    def _key_down(self, _window, keycode, _scancode, _codepoint, _modifiers):
        name = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        key = KEY_CODES.get(name)
        if key is not None:
            self.game.kivy_keys_down.add(key)
            self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
            return True
        return False

    def _key_up(self, _window, keycode, *_args):
        name = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        key = KEY_CODES.get(name)
        if key is not None:
            self.game.kivy_keys_down.discard(key)
            return True
        return False

    def on_stop(self):
        if hasattr(self, "game"):
            self.game.audio.close()
        pygame.quit()


if __name__ == "__main__":
    RailOperatorApp().run()
