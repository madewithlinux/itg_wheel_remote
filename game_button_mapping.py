from adafruit_hid.keycode import Keycode

KC_TRANSPARENT = KC_TRNS = _______ = (0x0001,)
KC_NO = XXXXXXX = (0x0000,)

# fmt: off
# # default P1 mappings
# ITG_KEYCODE_P1_MENU_LEFT   = Keycode.DELETE
# ITG_KEYCODE_P1_MENU_RIGHT  = Keycode.PAGE_DOWN
# ITG_KEYCODE_P1_MENU_UP     = Keycode.HOME
# ITG_KEYCODE_P1_MENU_DOWN   = Keycode.END
# ITG_KEYCODE_P1_LEFT        = Keycode.LEFT_ARROW
# ITG_KEYCODE_P1_RIGHT       = Keycode.RIGHT_ARROW
# ITG_KEYCODE_P1_UP          = Keycode.UP_ARROW
# ITG_KEYCODE_P1_DOWN        = Keycode.DOWN_ARROW

# my mappings. note: these are intentionally swapped for P1!
ITG_KEYCODE_P1_MENU_LEFT   = Keycode.LEFT_ARROW
ITG_KEYCODE_P1_MENU_RIGHT  = Keycode.RIGHT_ARROW
ITG_KEYCODE_P1_MENU_UP     = Keycode.UP_ARROW
ITG_KEYCODE_P1_MENU_DOWN   = Keycode.DOWN_ARROW
ITG_KEYCODE_P1_LEFT        = Keycode.DELETE
ITG_KEYCODE_P1_RIGHT       = Keycode.PAGE_DOWN
ITG_KEYCODE_P1_UP          = Keycode.HOME
ITG_KEYCODE_P1_DOWN        = Keycode.END

ITG_KEYCODE_P1_START       = Keycode.ENTER
ITG_KEYCODE_P1_SELECT      = Keycode.FORWARD_SLASH
ITG_KEYCODE_P1_BACK        = Keycode.ESCAPE
#
ITG_KEYCODE_P2_MENU_LEFT   = Keycode.KEYPAD_FORWARD_SLASH
ITG_KEYCODE_P2_MENU_RIGHT  = Keycode.KEYPAD_ASTERISK
ITG_KEYCODE_P2_MENU_UP     = Keycode.KEYPAD_MINUS
ITG_KEYCODE_P2_MENU_DOWN   = Keycode.KEYPAD_PLUS
ITG_KEYCODE_P2_LEFT        = Keycode.KEYPAD_FOUR
ITG_KEYCODE_P2_RIGHT       = Keycode.KEYPAD_SIX
ITG_KEYCODE_P2_UP          = Keycode.KEYPAD_EIGHT
ITG_KEYCODE_P2_DOWN        = Keycode.KEYPAD_TWO
ITG_KEYCODE_P2_START       = Keycode.KEYPAD_ENTER
ITG_KEYCODE_P2_SELECT      = Keycode.KEYPAD_ZERO
ITG_KEYCODE_P2_BACK        = Keycode.BACKSLASH
#
ITG_KEYCODE_OPERATOR       = Keycode.SCROLL_LOCK
# ITG_KEYCODE_COIN           = Keycode.F1
# fmt: on


class ItgPlayer:
    def __init__(self, value: int) -> None:
        self.value = value


class ItgButton:
    def __init__(self, value: int) -> None:
        self.value = value


# fmt: off
PLAYER_1 = ItgPlayer(0)
PLAYER_2 = ItgPlayer(1)

LEFT     = ItgButton(0)
RIGHT    = ItgButton(1)
UP       = ItgButton(2)
DOWN     = ItgButton(3)
START    = ItgButton(4)
SELECT   = ItgButton(5)
BACK     = ItgButton(6)
OPERATOR = ItgButton(7)
# COIN     = ItgButton(8)
# fmt: on

P1_MENU_BUTTONS = (
    ITG_KEYCODE_P1_MENU_LEFT,
    ITG_KEYCODE_P1_MENU_RIGHT,
    ITG_KEYCODE_P1_MENU_UP,
    ITG_KEYCODE_P1_MENU_DOWN,
    ITG_KEYCODE_P1_START,
    ITG_KEYCODE_P1_SELECT,
    ITG_KEYCODE_P1_BACK,
    ITG_KEYCODE_OPERATOR,
)
P1_GAME_BUTTONS = (
    ITG_KEYCODE_P1_LEFT,
    ITG_KEYCODE_P1_RIGHT,
    ITG_KEYCODE_P1_UP,
    ITG_KEYCODE_P1_DOWN,
    ITG_KEYCODE_P1_START,
    ITG_KEYCODE_P1_SELECT,
    ITG_KEYCODE_P1_BACK,
    ITG_KEYCODE_OPERATOR,
)
P2_MENU_BUTTONS = (
    ITG_KEYCODE_P2_MENU_LEFT,
    ITG_KEYCODE_P2_MENU_RIGHT,
    ITG_KEYCODE_P2_MENU_UP,
    ITG_KEYCODE_P2_MENU_DOWN,
    ITG_KEYCODE_P2_START,
    ITG_KEYCODE_P2_SELECT,
    ITG_KEYCODE_P2_BACK,
    ITG_KEYCODE_OPERATOR,
)
P2_GAME_BUTTONS = (
    ITG_KEYCODE_P2_LEFT,
    ITG_KEYCODE_P2_RIGHT,
    ITG_KEYCODE_P2_UP,
    ITG_KEYCODE_P2_DOWN,
    ITG_KEYCODE_P2_START,
    ITG_KEYCODE_P2_SELECT,
    ITG_KEYCODE_P2_BACK,
    ITG_KEYCODE_OPERATOR,
)


def get_itg_keycode_for_button(
    button: ItgButton, player_switch_value: bool, menu=True
) -> int:
    """NOTE: for player_switch_value, P1 is True, P2 is False"""
    if menu:
        if player_switch_value:  # P1
            return P1_MENU_BUTTONS[button.value]
        else:  # P2
            return P2_MENU_BUTTONS[button.value]
    else:
        if player_switch_value:  # P1
            return P1_GAME_BUTTONS[button.value]
        else:  # P2
            return P2_GAME_BUTTONS[button.value]
