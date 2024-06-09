# BLE_OVERRIDE = False
BLE_OVERRIDE = True

# USE_BLE_UART = False
USE_BLE_UART = True


import supervisor
from adafruit_hid.keyboard import Keyboard
from adafruit_ble.services.nordic import UARTService
from adafruit_ble import BLERadio

device_name = "ITG wheel remote v2.0"
manufacturer = "madewithlinux"


UARTService._server_tx._timeout = 0.00
UARTService._server_rx._timeout = 0.00


class UartKeyboard:
    def __init__(self, ble: BLERadio, uart: UARTService):
        self.ble = ble
        self.uart = uart

    def press(self, *keycodes: int) -> None:
        if not self.uart or not self.ble.connected:
            return
        for kc in keycodes:
            self.uart.write(f"P{kc}\n".encode("utf-8"))

    def release(self, *keycodes: int) -> None:
        if not self.uart or not self.ble.connected:
            return
        for kc in keycodes:
            self.uart.write(f"R{kc}\n".encode("utf-8"))


def _nop():
    pass


def get_hid_keyboard() -> (Keyboard, callable):
    """returns keyboard and function to poll in case of disconnects"""

    if not BLE_OVERRIDE and supervisor.runtime.usb_connected:
        print("using USB HID keyboard")
        import usb_hid

        return (Keyboard(usb_hid.devices), _nop)
    else:  # BLE_OVERRIDE
        import time
        import digitalio, board
        import adafruit_ble
        from adafruit_ble.advertising import Advertisement
        from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
        from adafruit_ble.services.standard.hid import HIDService
        from adafruit_ble.services.nordic import UARTService
        from adafruit_ble.services.standard.device_info import DeviceInfoService

        device_info = DeviceInfoService(
            software_revision=adafruit_ble.__version__,
            manufacturer=manufacturer,
            model_number=device_name,
        )
        ble = adafruit_ble.BLERadio()
        ble.name = device_name
        print(f"{ble._adapter.address=}")
        print(f"{repr(ble._adapter.address.address_bytes)=}")
        print(f"{repr(ble._adapter.address.type)=}")
        # print(f"{repr(ble._adapter.address.PUBLIC)=}")
        print(f"{repr(ble._adapter.address.RANDOM_STATIC)=}")
        # print(f"{repr(ble._adapter.address.RANDOM_PRIVATE_RESOLVABLE)=}")
        print(f"{ble.address_bytes=}")

        if USE_BLE_UART:
            print("using BLE UART keyboard")
            uart = UARTService()
            advertisement = ProvideServicesAdvertisement(uart, device_info)
            scan_response = Advertisement()
            scan_response.complete_name = device_name
        else:
            print("using BLE HID keyboard")
            hid = HIDService()
            advertisement = ProvideServicesAdvertisement(hid, device_info)
            # Advertise as "Keyboard" (0x03C1) icon when pairing
            # https://www.bluetooth.com/specifications/assigned-numbers/
            advertisement.appearance = 961
            scan_response = Advertisement()
            scan_response.complete_name = device_name

        # assume that any existing connections are stale, and disconnect from them
        for con in ble.connections:
            print("disconnecting from", con)
            con.disconnect()
        print("advertising")
        ble.stop_advertising()
        ble.start_advertising(advertisement, scan_response)

        # if not ble.connected:
        #     print("advertising")
        #     ble.stop_advertising()
        #     ble.start_advertising(advertisement, scan_response)
        # else:
        #     print("already connected")
        #     print(ble.connections)

        def block_until_connected():
            if ble.connected:
                return
            ble.stop_advertising()
            print("advertising")
            ble.start_advertising(advertisement, scan_response)
            # if not ble.advertising:
            #     print("advertising")
            #     ble.start_advertising(advertisement, scan_response)
            print("waiting for BLE connection")
            with digitalio.DigitalInOut(board.LED) as board_led:
                board_led.direction = digitalio.Direction.OUTPUT
                while not ble.connected:
                    board_led.value = True
                    time.sleep(0.1)
                    board_led.value = False
                    time.sleep(0.1)
            print("connected")
            ble.stop_advertising()

        if USE_BLE_UART:
            uart_ble_keyboard = UartKeyboard(ble, uart)

            block_until_connected()
            # create bonds so that next pair will be faster
            for connection in ble.connections:
                connection.pair(bond=True)
                print("bonded with", connection)
            return (uart_ble_keyboard, block_until_connected)

        if not USE_BLE_UART:
            print("using BLE HID keyboard")
            ble_hid_keyboard = Keyboard(hid.devices)
            # kl = KeyboardLayoutUS(k)

            block_until_connected()
            # create bonds so that next pair will be faster
            for connection in ble.connections:
                connection.pair(bond=True)
                print("bonded with", connection)
            return (ble_hid_keyboard, block_until_connected)
