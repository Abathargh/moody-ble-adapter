# moody-ble-adapter

A moody adapter for BLE nodes written in Python. It's used to tunnel data coming 
through BLE from an Arduino Nano 33 Sense.

The embedded sensors on the board are mapped as BLE services, while the data they read from the 
environment are mapped as observable characteristics. This application reads subscribes to the 
characteristics and maps them onto moody MQTT topics, to forward to the gateway.
