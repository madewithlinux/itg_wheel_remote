import hid_provider
from game_button_mapping import (
    ITG_KEYCODE_P1_MENU_LEFT,
    ITG_KEYCODE_P1_MENU_RIGHT,
    ITG_KEYCODE_P1_LEFT,
    ITG_KEYCODE_P1_RIGHT,
    ITG_KEYCODE_P1_UP,
    ITG_KEYCODE_P1_DOWN,
    ITG_KEYCODE_P2_MENU_LEFT,
    ITG_KEYCODE_P2_MENU_RIGHT,
    ITG_KEYCODE_P2_LEFT,
    ITG_KEYCODE_P2_RIGHT,
    ITG_KEYCODE_P2_UP,
    ITG_KEYCODE_P2_DOWN,
    KC_TRANSPARENT,
    KC_TRNS,
    _______,
    KC_NO,
    XXXXXXX,
    ItgButton,
    get_itg_keycode_for_button,
    LEFT,
    RIGHT,
    UP,
    DOWN,
    START,
    SELECT,
    BACK,
    OPERATOR,
)
import keypad_layout
from keypad_layout import layout

import time
import board, keypad, rotaryio, digitalio, analogio

from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS


class ItgWheelKeyboard:
    def __init__(self, keyboard: Keyboard, poll: callable) -> None:
        self.keyboard = keyboard
        self.poll = poll
        self.keyboard_layout = KeyboardLayoutUS(keyboard)

        self.keys = keypad.KeyMatrix(
            row_pins=(
                board.P0_17,
                board.P0_20,
                board.P0_22,
                board.P0_24,
            ),
            column_pins=(
                board.P0_08,
                board.P0_10,
                board.P0_09,
            ),
        )
        self.encoder = rotaryio.IncrementalEncoder(board.P1_06, board.P1_04, divisor=2)
        self.encoder_key = keypad.Keys(
            (board.P1_00,), value_when_pressed=False, pull=True
        )


        self.player_switch = digitalio.DigitalInOut(board.P0_11)
        """NOTE: for player_switch.value, P1 is True, P2 is False"""

        self.player_switch.switch_to_input(pull=digitalio.Pull.UP)
        self.bat_volt = analogio.AnalogIn(board.BAT_VOLT)

        # Define HID:
        self._keyboard = None
        self._consumer_control = None

        self.layers = []
        self.layer_index = 0
        self.layer_index_stack = []

    def _pick_by_active_player(self, p1_choice, p2_choice):
        if self.player_switch.value:
            return p1_choice
        else:
            return p2_choice

    def main_loop(self):
        event = keypad.Event()
        last_position = self.encoder.position
        while True:

            position = self.encoder.position
            if last_position != position:
                delta = position - last_position
                if delta > 0:
                    key_number = keypad_layout.INDEX_ENCODER_CW
                else:
                    key_number = keypad_layout.INDEX_ENCODER_CCW
                keycode = self.get_keycode(key_number)
                # TODO: should we preserve missed steps?
                # for i in range(abs(delta)):
                #     self.handle_keycode(keycode, True)
                #     time.sleep(0.01)
                #     self.handle_keycode(keycode, False)
                #     time.sleep(0.01)
                self.handle_keycode(keycode, True)
                time.sleep(0.01)
                self.handle_keycode(keycode, False)
                last_position = position

            if self.keys.events.get_into(event):
                # print("key event", event)
                keycode = self.get_keycode(event.key_number)
                self.handle_keycode(keycode, event.pressed)
                # print("layer state", self.layer_index, self.layer_index_stack)

            if self.encoder_key.events.get_into(event):
                keycode = self.get_keycode(keypad_layout.INDEX_ENCODER_MIDDLE)
                self.handle_keycode(keycode, event.pressed)

            self.poll()
            time.sleep(0.02)

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

    def handle_keycode(self, keycode: Union[int, ItgButton, callable], pressed: bool):
        if keycode is None or keycode is KC_NO:
            return
        if isinstance(keycode, ItgButton):
            keycode = get_itg_keycode_for_button(keycode, self.player_switch.value)
        if isinstance(keycode, int):
            if pressed:
                self.keyboard.press(keycode)
            else:
                self.keyboard.release(keycode)
        elif callable(keycode):
            keycode(pressed)
        else:
            print("error: unhandled keycode", keycode, type(keycode))

    def MO(self, layer_index: int):
        """activates layer as long as button is held"""

        # def fun(event: keypad.Event, *args, **kwargs):
        def fun(pressed: bool):
            if pressed:
                self.layer_index_stack.append(self.layer_index)
                self.layer_index = layer_index
            else:
                self.layer_index = self.layer_index_stack.pop()

        return fun

    def DF(self, layer_index: int):
        """immediately replaces current layer with target layer"""

        def fun(pressed: bool):
            if pressed:
                self.layer_index = layer_index

        return fun

    def ALL(self, *keycodes: int):

        def fun(pressed: bool):
            if pressed:
                self.keyboard.press(*keycodes)
            else:
                self.keyboard.release(*keycodes)

        return fun

    def BOOTLOADER(self, pressed: bool):
        if pressed:
            print("rebooting to bootloader")
            import microcontroller

            microcontroller.on_next_reset(microcontroller.RunMode.UF2)
            microcontroller.reset()

    def OPEN_MENU(self, pressed: bool):
        keycodes = self._pick_by_active_player(
            (
                ITG_KEYCODE_P1_MENU_LEFT,
                # ITG_KEYCODE_P1_LEFT,
                ITG_KEYCODE_P1_MENU_RIGHT,
                # ITG_KEYCODE_P1_RIGHT,
            ),
            (
                ITG_KEYCODE_P2_MENU_LEFT,
                # ITG_KEYCODE_P2_LEFT,
                ITG_KEYCODE_P2_MENU_RIGHT,
                # ITG_KEYCODE_P2_RIGHT,
            ),
        )
        if pressed:
            self.keyboard.press(*keycodes)
        else:
            self.keyboard.release(*keycodes)

    def CLOSE_FOLDER(self, pressed: bool):
        keycodes = self._pick_by_active_player(
            (
                ITG_KEYCODE_P1_UP,
                ITG_KEYCODE_P1_DOWN,
            ),
            (
                ITG_KEYCODE_P2_UP,
                ITG_KEYCODE_P2_DOWN,
            ),
        )
        if pressed:
            self.keyboard.press(*keycodes)
        else:
            self.keyboard.release(*keycodes)

    def FAVORITE(self, pressed: bool):
        keycode = self._pick_by_active_player(
            Keycode.I,
            Keycode.O,
        )
        if pressed:
            self.keyboard.press(keycode)
        else:
            self.keyboard.release(keycode)

    def BATT(self, pressed: bool):
        if pressed:
            val = self.bat_volt.value
            ref = self.bat_volt.reference_voltage
            volt = (val * ref) / 65535
            self.keyboard_layout.write(f"{val=}\n{ref=}\n{volt=}\n")


base_kb, poll = hid_provider.get_hid_keyboard()
kb = ItgWheelKeyboard(base_kb, poll)


# TODO
IR_SOUNDBAR_TOGGLE_MUTE = KC_NO
IR_SOUNDBAR_VOL_UP = KC_NO
IR_TV_POWER_ON_OFF = KC_NO
IR_SOUNDBAR_VOL_DOWN = KC_NO
IR_SOUNDBAR_POWER_ON_OFF = KC_NO
IR_TV_HDMI3 = KC_NO

QK_BOOT = kb.BOOTLOADER
ALT_F4 = kb.ALL(Keycode.ALT, Keycode.F4)
CLOSE_FOLDER = kb.CLOSE_FOLDER
OPEN_MENU = kb.OPEN_MENU
FAVORITE = kb.FAVORITE
PROFILE = Keycode.P


LAYER_PLAYER = 0
LAYER_FN = 1
LAYER_TEST = 2

# empty_layer = (KC_TRANSPARENT) * keypad_layout.LAYOUT_SIZE
kb.layers = (
    # fmt: off
    # LAYER_PLAYER
    layout(
        LEFT, RIGHT,
              UP    ,
        LEFT, START , RIGHT,
              DOWN  ,

        CLOSE_FOLDER    , OPEN_MENU,
        SELECT          , FAVORITE,
        BACK            , PROFILE,
        kb.MO(LAYER_FN) , XXXXXXX
    ),
    # LAYER_FN
    layout(
        IR_SOUNDBAR_VOL_DOWN, IR_SOUNDBAR_VOL_UP,
                 _______,
        _______, IR_SOUNDBAR_TOGGLE_MUTE, _______,
                 _______,

        QK_BOOT, ALT_F4  ,
        kb.BATT, OPERATOR,
        _______, _______ ,
        _______, _______ ,
    ),
    # LAYER_TEST
    layout(
        Keycode.L, Keycode.R,
        Keycode.ONE,   Keycode.TWO,   Keycode.THREE,
        Keycode.FOUR,  Keycode.FIVE,  Keycode.SIX,
        Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE,
        Keycode.A,     Keycode.B,     Keycode.C,
        kb.MO(LAYER_TEST),
    ),
    # fmt: on
)


def main():
    try:
        kb.main_loop()
    except ConnectionError as e:
        print("ConnectionError", e)
        import microcontroller, supervisor

        if supervisor.runtime.usb_connected:
            supervisor.reload()
        else:
            microcontroller.reset()
