try:
    from typing import Iterator, NoReturn, Optional, Tuple, Type, TYPE_CHECKING, Union
    from typing_extensions import Literal
except ImportError:
    pass


import _bleio

from adafruit_ble.services import Service
from adafruit_ble.characteristics import (
    Attribute,
    Characteristic,
    ComplexCharacteristic,
)
from adafruit_ble.characteristics.stream import BoundWriteStream
from adafruit_ble.characteristics.int import Int8Characteristic
from adafruit_ble.uuid import VendorUUID


class KeycodeCharacteristic(ComplexCharacteristic):
    # TODO: should these also have Characteristic.WRITE_NO_RESPONSE?
    def __init__(
        self,
        *,
        uuid,
        properties=Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        **kwargs,
    ) -> None:
        super().__init__(
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            max_length=6,
            fixed_length=True,
            **kwargs,
        )

    def bind(self, service):
        """Binds the characteristic to the given Service."""
        bound_characteristic = super().bind(service)
        # If the service is remote need to write out.
        if service.remote:
            return BoundWriteStream(bound_characteristic)
        return _bleio.CharacteristicBuffer(bound_characteristic, timeout=0.02)
        # return _bleio.CharacteristicBuffer(bound_characteristic)


class KeyProxyService(Service):
    uuid = VendorUUID("8c1ec0b3-a113-48ce-8d7b-d2d929da3243")

    # TODO: should these also have Characteristic.WRITE_NO_RESPONSE?
    key_press = KeycodeCharacteristic(
        uuid=VendorUUID("52a08193-e029-4cf8-9192-3fa151294cef"),
        # properties=Characteristic.WRITE,
    )

    key_release = KeycodeCharacteristic(
        uuid=VendorUUID("563e43f7-7995-4677-a5c0-e3e863081650"),
        # properties=Characteristic.WRITE,
    )

    def __init__(self, service=None):
        super().__init__(service=service)
        self.connectable = True

    def press(self, *keycodes: int) -> None:
        self.key_press.write(bytes(keycodes))
        # for kc in keycodes:
        #     print(f"{kc=}")
        #     self.key_press.write(kc.to_bytes(1, "big"))

    def release(self, *keycodes: int) -> None:
        self.key_release.write(bytes(keycodes))
        # for kc in keycodes:
        #     print(f"{kc=}")
        #     self.key_release.write(kc.to_bytes(1, "big"))

    def get_press(self) -> Optional[int]:
        buf = self.key_press.read(1)
        if buf:
            return buf[0]

    def get_release(self) -> Optional[int]:
        buf = self.key_release.read(1)
        if buf:
            return buf[0]
