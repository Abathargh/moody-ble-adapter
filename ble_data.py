from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from threading import Thread
import struct


class SensorWrapper(Thread):
    def __init__(self, mac):
        Thread.__init__(self)
        self._mac = mac

    def run(self):
        with Peripheral(self._mac) as peripheral:
            # get services
            # get and set the name and observe handler of characteristic
            pass


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self._dev_list = []

    @property
    def dev_list(self):
        return self._dev_list

    def handleDiscovery(self, dev, is_new_dev, is_new_data):
        if is_new_dev:
            self._dev_list.append(dev.addr)


class PrintDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, c_handle, data):
        # Little endian int, type could be obtained by type characteristic
        unp_data = struct.unpack("<b", data)[0]
        print(unp_data)


def scan(seconds):
    scanner = Scanner().withDelegate(ScanDelegate())
    devs = scanner.scan(seconds)
    return devs


def get_services(periph):
    for s in periph.getServices():
        print(s.uuid)
        print(f"\t{[str(c.uuid) for c in s.getCharacteristics()]}")


def list_devices(device_list):
    for device in device_list:
        print("Device %s (%s), RSSI=%d dB" % (device.addr, device.addrType, device.rssi))
        for (adtype, desc, value) in device.getScanData():
            print("  %s = %s" % (desc, value))
    print()


if __name__ == "__main__":
    running = True
    target = "e0:33:50:68:83:58"

    devices = scan(5)

    if target in [dev.addr for dev in devices]:
        try:
            with Peripheral(target) as peripheral:
                get_services(peripheral)
                battery_service = peripheral.getServiceByUUID("0000180f-0000-1000-8000-00805f9b34fb")
                battery_level_char = battery_service.getCharacteristics("00002a19-0000-1000-8000-00805f9b34fb")[0]
                peripheral.setDelegate(PrintDelegate())
                peripheral.writeCharacteristic(battery_level_char.valHandle + 1, b"\x01\x00")
                while running:
                    peripheral.waitForNotifications(5)
        except KeyboardInterrupt:
            running = False
