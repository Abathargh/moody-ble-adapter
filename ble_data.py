from bluepy.btle import Scanner, DefaultDelegate, Peripheral


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, is_new_dew, is_new_data):
        if is_new_dew:
            print("Discovered device", dev.addr)
        elif is_new_data:
            print("Received new data from", dev.addr)


def scan(seconds):
    scanner = Scanner().withDelegate(ScanDelegate())
    devs = scanner.scan(seconds)

    return devs


def get_services(mac):
    with Peripheral(mac) as p:
        for s in p.getServices():
            print(s.uuid)
            print(f"\t{[c.__dict__ for c in s.getCharacteristics()]}")


if __name__ == "__main__":
    devices = scan(5)
    for device in devices:
        print("Device %s (%s), RSSI=%d dB" % (device.addr, device.addrType, device.rssi))
        for (adtype, desc, value) in device.getScanData():
            print("  %s = %s" % (desc, value))
    print()
    target = "e0:33:50:68:83:58"
    if target in [dev.addr for dev in devices]:
        get_services(target)
