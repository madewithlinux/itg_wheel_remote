import time
import digitalio, board, usb_hid, microcontroller, supervisor

import adafruit_ble
from adafruit_hid.keyboard import Keyboard
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.services.standard.device_info import DeviceInfoService


kb = Keyboard(usb_hid.devices)
ble = BLERadio()

# reduce BLE uart latency
UARTService._server_tx._timeout = 0.01
UARTService._server_rx._timeout = 0.01

uart_connection = None
buf = bytearray(512)


board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT

button = digitalio.DigitalInOut(board.P0_22)
button.pull = digitalio.Pull.UP

def poll_for_reset():
    if not button.value:
        print('reset button pressed')
        if supervisor.runtime.usb_connected:
            supervisor.reload()
        else:
            microcontroller.reset()


while True:
    if not uart_connection:
        board_led.value = True
        print("Trying to connect...")
        for adv in ble.start_scan(ProvideServicesAdvertisement):
            if UARTService in adv.services:
                uart_connection = ble.connect(adv)
                uart_connection.pair(bond=True)
                # print(f'{dir(adv)=}')
                print("Connected to", adv.short_name, adv.complete_name, adv.address)
                break
        ble.stop_scan()
        board_led.value = False

    if uart_connection and uart_connection.connected:
        uart_service = uart_connection[UARTService]
        while uart_connection.connected:
            msg_bytes = uart_service.read(16)
            poll_for_reset()
            if not msg_bytes:
                continue
            # print(repr(msg))
            msg = msg_bytes.decode("utf-8").rstrip("\n")
            # print(repr(msg))
            for line in msg.split('\n'):
                try:
                    inst = line[0]
                    if inst == "P":
                        keycode = int(line[1:])
                        kb.press(keycode)
                        time.sleep(0.02)
                    elif inst == "R":
                        keycode = int(line[1:])
                        kb.release(keycode)
                        time.sleep(0.02)
                except:
                    print("failed to parse", repr(line))
                board_led.value = not board_led.value
        kb.release_all()
