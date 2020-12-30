from sensor import MoodySensor

count = 0
cert_path = "/home/mar/GolandProjects/moody-go/broker/ca.crt"


def count_service():
    global count
    count = 0 if count == 255 else count + 1
    return count


def main():
    sensor = MoodySensor("count", count_service, cert_path, 5)
    try:
        sensor.begin("moodybase", 8883)
    except KeyboardInterrupt:
        sensor.stop()


if __name__ == "__main__":
    main()
