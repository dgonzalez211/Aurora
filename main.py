from umqtt.simple import MQTTClient
from machine import Pin
import RPi.GPIO as GPIO
import serial
import network
import time
import ds18x20
import onewire

CAYENNE_TOKEN = None
WIFI_SSID = "FLIA GONZALEZ"
WIFI_PASSWORD = "4905A233ECAE4B37"

reading = 0
high_score = 0
last_state = 0

Serial = serial.Serial(
    port="COM8",
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# the MQ3 device is on GPIO12
dat = Pin(12)
# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))
# scan for devices on the bus
roms = ds.scan()

print('found devices:', roms)

# CAYENNE GLOBAL CONFIGURATION
SERVER = "mqtt.mydevices.com"
CLIENT_ID = "fef9a370-02b6-11ed-bbc1-5d0b0fa0a668"  # Client Id for Cayenne
username = "f8bb47c0-02b6-11ed-bbc1-5d0b0fa0a668"  # The Cayenne MQTT username
password = "b37117afefd888277fe542025346dd002db2f990"  # The Cayenne MQTT password
TOPIC = ("v1/%s/things/%s/data/1" % (username, CLIENT_ID))

server = SERVER
cayenne = MQTTClient(CLIENT_ID, server, 0, username, password)
cayenne.connect()

"""
   FUNCIONES UTILITARIAS
"""

# This sends the datathrough cayenne my devices mqtt api
def send_data():
    time.sleep_ms(100)
    alcohol = ds.measure(roms[0])
    cayenne.publish(TOPIC, str(alcohol))

    time.sleep(10)
    print("Current alcohol measure is: ", alcohol)
    print("data sent")


def do_connect(SSID, PASSWORD):
    global sta_if
    # Instanciamos el objeto -sta_if- para controlar la interfaz STA
    sta_if = network.WLAN(network.STA_IF)
    # COMIENZA EL BUCLE - SI NO EXISTE CONEXION
    if not sta_if.isconnected():
        # Activamos el interfaz STA del ESP32
        sta_if.active(True)
        # Iniciamos la conexion con el AP
        sta_if.connect(SSID, PASSWORD)
        print('Connecting to ', SSID + "...")
        # SI NO SE ESTABLECE
        while not sta_if.isconnected():
            # REPITE EL BUCLE
            pass
    # MUESTRA EN PANTALLA
    print('NETWORK CONFIG (IP/MASK/GATEWAY/DNS:', sta_if.ifconfig())


print("Booting code...")

do_connect(WIFI_SSID, WIFI_PASSWORD)

while True:
    try:
        send_data()
    except OSError:
        pass
