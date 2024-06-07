# BLE_ENABLED = True
BLE_ENABLED = False
import supervisor
from adafruit_hid.keyboard import Keyboard

device_name = "ITG wheel remote v2.0"
manufacturer = "madewithlinux"


def get_hid_keyboard() -> Keyboard:

    if not BLE_ENABLED and supervisor.runtime.usb_connected:
        import usb_hid

        return Keyboard(usb_hid.devices)
    else:  # BLE_ENABLED
        import time
        import digitalio, board
        import adafruit_ble
        from adafruit_ble.advertising import Advertisement
        from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
        from adafruit_ble.services.standard.hid import HIDService
        from adafruit_ble.services.standard.device_info import DeviceInfoService

        hid = HIDService()
        device_info = DeviceInfoService(
            software_revision=adafruit_ble.__version__,
            manufacturer=manufacturer,
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

        with digitalio.DigitalInOut(board.LED) as board_led:
            board_led.direction = digitalio.Direction.OUTPUT
            while not ble.connected:
                board_led.value = True
                time.sleep(0.1)
                board_led.value = False
                time.sleep(0.1)
        return ble_keyboard
