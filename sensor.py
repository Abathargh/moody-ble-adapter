from paho.mqtt.client import Client
from random import randint
import time


class MoodySensor:
    base_topic = "moody/service/"

    def __init__(self, service_name, service_func, ca_crt, period=None):
        self._topic = f"{MoodySensor.base_topic}{service_name}"
        self._sfunc = service_func
        self._client = Client(f"Moody{randint(100, 999)}")
        self._client.tls_set(ca_certs=ca_crt)
        self._running = False
        self._period = 1 if period is None else period

    def _loop(self):
        self._running = True
        while self._running:
            payload = self._sfunc()
            self._client.publish(topic=self._topic, payload=payload, qos=0)
            print(f"published on topic {self._topic}, payload: {payload}")
            time.sleep(self._period)

    def begin(self, host, port=None):
        if not port:
            port = 8883
        self._client.connect(host=host, port=port)
        self._client.loop_start()

        self._loop()

    def stop(self):
        self._running = False
        self._client.loop_stop()
        self._client.disconnect()
