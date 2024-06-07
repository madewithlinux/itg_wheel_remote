import board, digitalio
import storage
import usb_midi

usb_midi.disable()

# ref https://learn.adafruit.com/welcome-to-circuitpython/renaming-circuitpy#renaming-circuitpy-through-circuitpython-3014813
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "ITG_WHEEL"
storage.remount("/", readonly=True)
storage.enable_usb_drive()

# # ref https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/circuitpy-midi-serial#dont-lock-yourself-out-3096636
# button = digitalio.DigitalInOut(board.GP7)
# button.pull = digitalio.Pull.UP
# if button.value:
#     storage.disable_usb_drive()
