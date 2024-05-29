import busio
import board
import digitalio
import displayio
import i2cdisplaybus
import keypad
import rotaryio

import adafruit_displayio_ssd1306
from adafruit_debouncer import Debouncer
import usb_hid, usb_cdc
import adafruit_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_base import KeyboardLayoutBase
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode


displayio.release_displays()

ROTA = board.GP18
ROTB = board.GP19
BUTTON = board.GP20

# See https://cdn-shop.adafruit.com/product-files/5228/5223-ds.pdf#page=13
_DISPLAY_SLEEP_COMMAND = 0xAE
_DISPLAY_WAKE_COMMAND = 0xAF


KC_TRANSPARENT = KC_TRNS = _______ = (0x0001,)
KC_NO = XXXXXXX = (0x0000,)


def create_bitmap_group(file_path: str):
    # https://learn.adafruit.com/circuitpython-display-support-using-displayio/display-a-bitmap
    # Setup the file as the bitmap data source
    bitmap = displayio.OnDiskBitmap(file_path)

    # Create a TileGrid to hold the bitmap
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)

    # Create a Group to hold the TileGrid
    group = displayio.Group()

    # Add the TileGrid to the Group
    group.append(tile_grid)
    return group


layer_image_paths = [
    "img/p1_menu_buttons.bmp",
    "img/p2_menu_buttons.bmp",
    "img/p1_game_buttons.bmp",
    "img/p2_game_buttons.bmp",
    "img/Fn.bmp",
]
layer_bitmap_groups = [
    create_bitmap_group(p) for p in layer_image_paths
]


class ItgWheelKeyboard:
    def __init__(
        self,
        layout_class: type[KeyboardLayoutBase] = KeyboardLayoutUS,
        keycode_class: type[Keycode] = Keycode,
    ) -> None:
        self.i2c = busio.I2C(board.GP3, board.GP2)
        self.display_bus = i2cdisplaybus.I2CDisplayBus(self.i2c, device_address=0x3C)
        self.display = adafruit_displayio_ssd1306.SSD1306(
            self.display_bus, width=128, height=64
        )
        if not isinstance(self.display, type(None)):
            self.display.bus.send(_DISPLAY_WAKE_COMMAND, b"")
        self._display_sleep = False

        self.keys = keypad.Keys(
            pins=(
                # fmt: off
                board.GP7,  board.GP5,  board.GP4,
                board.GP22, board.GP21, board.GP9,
                board.GP17, board.GP10, board.GP12,
                board.GP16, board.GP14, board.GP15,
                # fmt: on
            ),
            value_when_pressed=False,
            pull=True,
        )
        self._encoder = rotaryio.IncrementalEncoder(ROTA, ROTB)
        self._encoder_switch = digitalio.DigitalInOut(BUTTON)
        self._encoder_switch.switch_to_input(pull=digitalio.Pull.UP)
        self._debounced_switch = Debouncer(self._encoder_switch)

        # Define HID:
        self._keyboard = None
        self._keyboard_layout = None
        self._consumer_control = None
        # self._mouse = None
        self._layout_class = layout_class
        self.Keycode = keycode_class

        self.layers = []
        self.layer_index = 0
        self.layer_index_stack = []
        self.encoder_layers = []

    @property
    def keyboard(self) -> Keyboard:
        if self._keyboard is None:
            self._keyboard = Keyboard(usb_hid.devices)
        return self._keyboard

    @property
    def keyboard_layout(self) -> KeyboardLayoutBase:
        if self._keyboard_layout is None:
            # This will need to be updated if we add more layouts. Currently there is only US.
            self._keyboard_layout = self._layout_class(self.keyboard)
        return self._keyboard_layout

    @property
    def consumer_control(self) -> ConsumerControl:
        if self._consumer_control is None:
            self._consumer_control = ConsumerControl(usb_hid.devices)
        return self._consumer_control

    @property
    def encoder_position(self) -> int:
        return self._encoder.position

    def handle_encoder(self, delta: int):
        if delta > 0:
            key_number = 1
        else:
            key_number = 0
        keycode = self.get_keycode(key_number, layers=self.encoder_layers)
        if keycode is None or keycode is KC_NO:
            return
        elif isinstance(keycode, int):
            for i in range(abs(delta)):
                self.keyboard.send(keycode)
        elif callable(keycode):
            keycode(delta)
        else:
            print("error: unhandled keycode", keycode, type(keycode))

    def main_loop(self):
        event = keypad.Event()
        last_position = self.encoder_position
        self.on_layer_changed()
        while True:
            initial_layer_index = self.layer_index

            position = self.encoder_position
            if last_position != position:
                delta = position - last_position
                self.handle_encoder(delta)
            last_position = position
            if self.keys.events.get_into(event):
                # keycode = self.layers[self.layer_index][event.key_number]
                keycode = self.get_keycode(event.key_number)
                if keycode is None or keycode is KC_NO:
                    continue
                elif isinstance(keycode, int):
                    if event.pressed:
                        self.keyboard.press(keycode)
                    elif event.released:
                        self.keyboard.release(keycode)
                elif callable(keycode):
                    keycode(event)
                else:
                    print("error: unhandled keycode", keycode, type(keycode))
                print(f"{self.layer_index=} {self.layer_index_stack}")

            if self.layer_index != initial_layer_index:
                self.on_layer_changed()

    def on_layer_changed(self):
        if self.layer_index < len(layer_bitmap_groups):
            self.display.root_group = layer_bitmap_groups[self.layer_index]

    def get_keycode(self, key_number: int, layers: list = None):
        if layers is None:
            layers = self.layers
        keycode = layers[self.layer_index][key_number]
        if keycode is not KC_TRANSPARENT:
            return keycode
        for layer_index in self.layer_index_stack[::-1]:
            keycode = layers[layer_index][key_number]
            if keycode is not KC_TRANSPARENT:
                return keycode
        return None

    def MO(self, layer_index: int):
        """activates layer as long as button is held"""

        # def fun(event: keypad.Event, *args, **kwargs):
        def fun(event: keypad.Event):
            if event.pressed:
                self.layer_index_stack.append(self.layer_index)
                self.layer_index = layer_index
            elif event.released:
                self.layer_index = self.layer_index_stack.pop()

        return fun

    def DF(self, layer_index: int):
        """immediately replaces current layer with target layer"""

        def fun(event: keypad.Event):
            if event.pressed:
                self.layer_index = layer_index

        return fun

    def SEND(self, *keycodes: int):
        """immediately replaces current layer with target layer"""

        def func(event: keypad.Event):
            if event.pressed:
                self.keyboard.press(*keycodes)
            elif event.released:
                self.keyboard.release(*keycodes)

        return func

    def BOOTLOADER(self, event: keypad.Event):
        if event.pressed:
            print("rebooting to bootloader")
            import microcontroller

            microcontroller.on_next_reset(microcontroller.RunMode.UF2)
            microcontroller.reset()


kb = ItgWheelKeyboard()

# my mappings. note: these are intentionally swapped for P1!
# fmt: off
P1_MENU_LEFT   = Keycode.LEFT_ARROW
P1_MENU_RIGHT  = Keycode.RIGHT_ARROW
P1_MENU_UP     = Keycode.UP_ARROW
P1_MENU_DOWN   = Keycode.DOWN_ARROW
P1_LEFT        = Keycode.DELETE
P1_RIGHT       = Keycode.PAGE_DOWN
P1_UP          = Keycode.HOME
P1_DOWN        = Keycode.END
P1_START       = Keycode.ENTER
P1_SELECT      = Keycode.FORWARD_SLASH
P1_BACK        = Keycode.ESCAPE
#
P2_MENU_LEFT   = Keycode.KEYPAD_FORWARD_SLASH
P2_MENU_RIGHT  = Keycode.KEYPAD_ASTERISK
P2_MENU_UP     = Keycode.KEYPAD_MINUS
P2_MENU_DOWN   = Keycode.KEYPAD_PLUS
P2_LEFT        = Keycode.KEYPAD_FOUR
P2_RIGHT       = Keycode.KEYPAD_SIX
P2_UP          = Keycode.KEYPAD_EIGHT
P2_DOWN        = Keycode.KEYPAD_TWO
P2_START       = Keycode.KEYPAD_ENTER
P2_SELECT      = Keycode.KEYPAD_ZERO
P2_BACK        = Keycode.BACKSLASH
#
COIN           = Keycode.F1
OPERATOR       = Keycode.SCROLL_LOCK
# fmt: on

P1_OPEN_MENU = kb.SEND(P1_MENU_LEFT, P1_MENU_RIGHT)
P1_CLOSE = kb.SEND(P1_UP, P1_DOWN)
P2_OPEN_MENU = kb.SEND(P2_MENU_LEFT, P2_MENU_RIGHT)
P2_CLOSE = kb.SEND(P2_UP, P2_DOWN)

# TODO
IR_SOUNDBAR_TOGGLE_MUTE = KC_NO
IR_SOUNDBAR_VOL_UP = KC_NO
IR_TV_POWER_ON_OFF = KC_NO
IR_SOUNDBAR_VOL_DOWN = KC_NO
IR_SOUNDBAR_POWER_ON_OFF = KC_NO
IR_TV_HDMI3 = KC_NO
QK_BOOT = kb.BOOTLOADER
ALT_F4 = kb.SEND(Keycode.ALT, Keycode.F4)


LAYER_P1 = 0
LAYER_P2 = 1
LAYER_P1_GAME = 2
LAYER_P2_GAME = 3
LAYER_FN = 4
LAYER_TEST = 5

kb.encoder_layers = (
    # LAYER_P1
    (P1_MENU_LEFT, P1_MENU_RIGHT),
    # LAYER_P2
    (P2_MENU_LEFT, P2_MENU_RIGHT),
    # LAYER_P1_GAME
    (P1_LEFT, P1_RIGHT),
    # LAYER_P2_GAME
    (P2_LEFT, P2_RIGHT),
    # LAYER_FN
    (IR_SOUNDBAR_VOL_DOWN, IR_SOUNDBAR_VOL_UP),
    # LAYER_TEST
    (P1_MENU_LEFT, P1_MENU_RIGHT),
)

# fmt: off
empty_layer = (KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT)
# fmt: on
kb.layers = (
    # fmt: off
    # LAYER_P1
    (
        P1_SELECT   , P1_MENU_UP  , P1_START,
        P1_MENU_LEFT, P1_MENU_DOWN, P1_MENU_RIGHT,
        P1_OPEN_MENU, P1_CLOSE    , kb.DF(LAYER_P2),
        P1_BACK     , kb.MO(LAYER_P1_GAME), kb.MO(LAYER_FN)
    ),
    # LAYER_P2
    (
        P2_SELECT   , P2_MENU_UP  , P2_START,
        P2_MENU_LEFT, P2_MENU_DOWN, P2_MENU_RIGHT,
        P2_OPEN_MENU, P2_CLOSE    , kb.DF(LAYER_P1),
        P2_BACK     , kb.MO(LAYER_P2_GAME), kb.MO(LAYER_FN)
    ),
    # LAYER_P1_GAME
    (
        P1_SELECT   , P1_UP       , P1_START,
        P1_LEFT     , P1_DOWN     , P1_RIGHT,
        P1_OPEN_MENU, P1_CLOSE    , XXXXXXX,
        P1_BACK     , _______     , XXXXXXX
    ),
    # LAYER_P2_GAME
    (
        P2_SELECT   , P2_UP       , P2_START,
        P2_LEFT     , P2_DOWN     , P2_RIGHT,
        P2_OPEN_MENU, P2_CLOSE    , XXXXXXX,
        P2_BACK     , _______     , XXXXXXX
    ),
    # LAYER_FN
    (
        IR_SOUNDBAR_TOGGLE_MUTE , IR_SOUNDBAR_VOL_UP   , IR_TV_POWER_ON_OFF,
        _______                 , IR_SOUNDBAR_VOL_DOWN , IR_SOUNDBAR_POWER_ON_OFF,
        QK_BOOT                 , OPERATOR             , IR_TV_HDMI3,
        ALT_F4                  , _______              , _______
    ),
    # LAYER_TEST
    (
        Keycode.ONE,   Keycode.TWO,   Keycode.THREE,
        Keycode.FOUR,  Keycode.FIVE,  Keycode.SIX,
        Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE,
        Keycode.A,     Keycode.B,     kb.MO(LAYER_TEST),
    ),
    # fmt: on
)


def main():
    kb.main_loop()
