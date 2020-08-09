import uos as os
import utime as time
import ujson as json
import network
import machine
from dht import DHT11
from ubinascii import hexlify
import socket
import ustruct as struct

#this file contains network and config information
f = open('config.json', 'r')
config_file = json.load(f)
f.close()

#establish a wifi connection and print info
STA = network.WLAN(network.STA_IF)
STA.active(True)

if not STA.isconnected():
    print("connecting to network...")
    print(config_file['WLAN_SSID'])
    print(config_file['WLAN_PW'])
    STA.connect(config_file['WLAN_SSID'], config_file['WLAN_PW'])
if STA.isconnected():
    print('connected to network', config_file['WLAN_SSID'])
    print('network config:', STA.ifconfig())
STA.config(dhcp_hostname = hexlify(machine.unique_id(), ':').decode())

#adapted from https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/ntptime.py
def gettime():
    host = config_file['Time_Server']
    NTP_DELTA = 3155673600
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA

def settime():
    t = gettime()
    tm = time.localtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

def timestamp():
    t = time.localtime()
    return '{}-{}-{}T{}:{}:{}Z'.format(t[0], t[1], t[2], t[3], t[4], t[5])


def DHTlog():
    #set up a DHT11 sensor on GPIO pin 4
    d = DHT11(machine.Pin(4))
    d.measure()
    temp = float('{:.1f}'.format(d.temperature() ) * 1.8 + 32))  #convert to Fahrenheit
    humid = float('{:.1f}'.format(d.humidity()))
    #return a dictionary of (temp. humidity)
    return {'temp' : temp, 'humid' : humid}

def eventlog():
    d = DHTlog()
    hn = hexlify(machine.unique_id(), ':').decode()
    return {'id' : config_file['uuid'], 'event' : {'humdity' : d['humid'], 'temperature' : d['temp'], 'hostname' : hn, 'timestamp' : timestamp()}}

#get the time from a time server
settime()
host = config_file['Server_IP']
port = int(config_file['Server_Port'])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, 5000))

def transmit():
    event = eventlog()
    s.sendall(json.dumps(event))

while True:
    transmit()
    time.sleep(int(config_file['Granularity']))
