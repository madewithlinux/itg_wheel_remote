import game_button_mapping
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
    ItgPlayer,
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

import board
import keypad
import rotaryio
import digitalio
from time import sleep

# from adafruit_debouncer import Debouncer
import usb_hid, usb_cdc
import adafruit_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_base import KeyboardLayoutBase
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT

device_name = "ITG wheel remote v2.0"

# BLE_ENABLED = True
BLE_ENABLED = False
if BLE_ENABLED:
    import adafruit_ble
    from adafruit_ble.advertising import Advertisement
    from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
    from adafruit_ble.services.standard.hid import HIDService
    from adafruit_ble.services.standard.device_info import DeviceInfoService

    hid = HIDService()
    device_info = DeviceInfoService(
        software_revision=adafruit_ble.__version__,
        manufacturer="Adafruit Industries",
        model_number=device_name,
    )
    advertisement = ProvideServicesAdvertisement(hid, device_info)
    # Advertise as "Keyboard" (0x03C1) icon when pairing
    # https://www.bluetooth.com/specifications/assigned-numbers/
    advertisement.appearance = 961
    scan_response = Advertisement()
    scan_response.complete_name = device_name
    ble = adafruit_ble.BLERadio()
    ble.name = device_name

    if not ble.connected:
        print("advertising")
        ble.start_advertising(advertisement, scan_response)
    else:
        print("already connected")
        print(ble.connections)

    ble_keyboard = Keyboard(hid.devices)
    # kl = KeyboardLayoutUS(k)

    while not ble.connected:
        board_led.value = True
        sleep(0.1)
        board_led.value = False
        sleep(0.1)


class ItgWheelKeyboard:
    def __init__(
        self,
        layout_class: type[KeyboardLayoutBase] = KeyboardLayoutUS,
        keycode_class: type[Keycode] = Keycode,
    ) -> None:

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
        self.encoder = rotaryio.IncrementalEncoder(board.P1_06, board.P1_04)
        self.encoder_key = keypad.Keys(
            (board.P1_00,), value_when_pressed=False, pull=True
        )

        self.player_switch = digitalio.DigitalInOut(board.P0_11)
        """NOTE: for player_switch.value, P1 is True, P2 is False"""

        self.player_switch.switch_to_input(pull=digitalio.Pull.UP)

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

    @property
    def keyboard(self) -> Keyboard:
        if self._keyboard is None:
            if BLE_ENABLED:
                self._keyboard = ble_keyboard
            else:
                self._keyboard = Keyboard(usb_hid.devices)
        return self._keyboard

    @property
    def consumer_control(self) -> ConsumerControl:
        if self._consumer_control is None:
            self._consumer_control = ConsumerControl(usb_hid.devices)
        return self._consumer_control

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
                #     self.handle_keycode(keycode, False)
                self.handle_keycode(keycode, True)
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

            sleep(0.02)

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
        if self.player_switch.value:
            keycodes = (
                ITG_KEYCODE_P1_MENU_LEFT,
                ITG_KEYCODE_P1_LEFT,
                ITG_KEYCODE_P1_MENU_RIGHT,
                ITG_KEYCODE_P1_RIGHT,
            )
        else:
            keycodes = (
                ITG_KEYCODE_P2_MENU_LEFT,
                ITG_KEYCODE_P2_LEFT,
                ITG_KEYCODE_P2_MENU_RIGHT,
                ITG_KEYCODE_P2_RIGHT,
            )
        if pressed:
            self.keyboard.press(*keycodes)
        else:
            self.keyboard.release(*keycodes)

    def CLOSE_FOLDER(self, pressed: bool):
        if self.player_switch.value:
            keycodes = (
                ITG_KEYCODE_P1_UP,
                ITG_KEYCODE_P1_DOWN,
            )
        else:
            keycodes = (
                ITG_KEYCODE_P2_UP,
                ITG_KEYCODE_P2_DOWN,
            )
        if pressed:
            self.keyboard.press(*keycodes)
        else:
            self.keyboard.release(*keycodes)


kb = ItgWheelKeyboard()


# TODO
IR_SOUNDBAR_TOGGLE_MUTE = KC_NO
IR_SOUNDBAR_VOL_UP = KC_NO
IR_TV_POWER_ON_OFF = KC_NO
IR_SOUNDBAR_VOL_DOWN = KC_NO
IR_SOUNDBAR_POWER_ON_OFF = KC_NO
IR_TV_HDMI3 = KC_NO
QK_BOOT = kb.BOOTLOADER
ALT_F4 = kb.ALL(Keycode.ALT, Keycode.F4)


LAYER_PLAYER = 0
LAYER_FN = 1
LAYER_TEST = 2

empty_layer = (KC_TRANSPARENT) * keypad_layout.LAYOUT_SIZE
kb.layers = (
    # fmt: off
    # LAYER_PLAYER
    layout(
        LEFT, RIGHT,
              UP    ,
        LEFT, START , RIGHT,
              DOWN  ,
        kb.CLOSE_FOLDER , kb.OPEN_MENU,
        SELECT          , _______,
        BACK            , _______,
        kb.MO(LAYER_FN) , XXXXXXX
    ),
    # LAYER_FN
    layout(
        IR_SOUNDBAR_VOL_DOWN, IR_SOUNDBAR_VOL_UP,
                 _______,
        _______, IR_SOUNDBAR_TOGGLE_MUTE, _______,
                 _______,

        QK_BOOT, IR_SOUNDBAR_POWER_ON_OFF,
        _______, OPERATOR,
        _______, _______ ,
        _______, ALT_F4  ,
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
    import analogio

    bat_volt = analogio.AnalogIn(board.BAT_VOLT)
    print("battery value", bat_volt.value)
    print("ref", bat_volt.reference_voltage)
    print("battery:", (bat_volt.value * bat_volt.reference_voltage) / 65535)
    kb.main_loop()
