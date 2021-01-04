from bluepy.btle import Peripheral, Scanner, DefaultDelegate
from paho.mqtt.client import Client
from threading import Thread, Lock
from random import randint
import struct
import sys


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


class _MQTTDelegate(DefaultDelegate):
    base_topic = "moody/service/"

    def __init__(self, client, client_mutex, handle_map):
        DefaultDelegate.__init__(self)
        self._client_mutex = client_mutex
        self._client = client
        self._handle_map = handle_map

    def handleNotification(self, c_handle, data):
        # Little endian float unpacking
        with self._client_mutex:
            unp_data = struct.unpack("<f", data)[0]
            topic = f"{_MQTTDelegate.base_topic}{self._handle_map[c_handle]}"
            self._client.publish(topic=topic, payload=str("{:.1f}".format(unp_data)))


class MoodyBLEWrapper(Thread):
    def __init__(self, mac, host, ca_cert):
        Thread.__init__(self)
        self._mac = mac
        self._host = host
        self._ca_cert = ca_cert
        self._running = False

        self._mutex = Lock()
        self._client = Client(f"Moody{randint(100, 999)}")
        self._client.tls_set(ca_certs=ca_cert)

        # When receiving data with a delegate, you also receive a characteristic handle
        # This is a mapping of those characteristic for later usage
        self._handle_mappings = {}

    def run(self):
        self._running = True
        self._connect(host=self._host)
        with Peripheral(self._mac) as peripheral:
            for service in list(peripheral.getServices())[2:]:
                print(service, service.uuid.getCommonName())
                char_uuids = [str(c.uuid) for c in service.getCharacteristics()]
                name_char = service.getCharacteristics(char_uuids[0])[0]
                value_char = service.getCharacteristics(char_uuids[1])[0]

                service_name = name_char.read().decode()
                self._handle_mappings[value_char.valHandle] = service_name
                mqtt_delegate = _MQTTDelegate(client=self._client, client_mutex=self._mutex,
                                              handle_map=self._handle_mappings)

                peripheral.withDelegate(mqtt_delegate)
                peripheral.writeCharacteristic(value_char.valHandle + 1, b"\x01\x00")

            while self._running:
                peripheral.waitForNotifications(1)

            peripheral.disconnect()

    def _connect(self, host, port=None):
        if not port:
            port = 8883
        self._client.connect(host=host, port=port)
        self._client.loop_start()

    def stop(self):
        self._running = False
        self._client.loop_stop()
        self._client.disconnect()


def scan(seconds):
    scanner = Scanner().withDelegate(ScanDelegate())
    devs = scanner.scan(seconds)
    return devs


def list_devices(device_list):
    moody_device_list = {}
    for m_device in device_list:
        if m_device.addrType == "public":
            for (adtype, desc, value) in m_device.getScanData():
                if desc == "Complete Local Name" and "Moody" in value:
                    moody_device_list[m_device.addr] = value
    return moody_device_list


def main():
    if len(sys.argv) != 3:
        print("Only two arg expected ([1]host, [2]ca_crt)")
        return
    gw_host = sys.argv[1]
    cert_path = sys.argv[2]
    devices = scan(2)
    moody_devices = list_devices(devices)
    print(moody_devices)

    for device in moody_devices:
        MoodyBLEWrapper(device, gw_host, cert_path).start()


if __name__ == "__main__":
    main()
