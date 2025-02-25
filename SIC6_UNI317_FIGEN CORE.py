from machine import Pin, I2C
import ssd1306
import time
import dht
import network
import urequests

# 🔹 Konfigurasi WiFi
SSID = "Remukan_peyek"
PASSWORD = "Bosse12345"

# 🔹 Konfigurasi API Ubidots
UBIDOTS_TOKEN = "BBUS-MxJqqKUKdVBnCtlmnWibz9Gotwwaxo"
UBIDOTS_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/IOT_ESP32_UNI317/"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# 🔹 Koneksi WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        pass
    print("WiFi Connected:", wlan.ifconfig())

# 🔹 Setup I2C untuk OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# 🔹 Setup Sensor DHT11
dht_sensor = dht.DHT11(Pin(4))  # DHT11 di GPIO4

# 🔹 Setup LED dan Buzzer
led_red = Pin(18, Pin.OUT)  # LED merah di GPIO18
led_yellow = Pin(5, Pin.OUT)  # LED kuning di GPIO5
buzzer = Pin(2, Pin.OUT)  # Buzzer di GPIO2

# 🔹 Kirim Data ke Ubidots
def send_data(temp, hum):
    data = {
        "suhu_kompos": temp,
        "kelembaban_kompos": hum
    }
    try:
        response = urequests.post(UBIDOTS_URL, json=data, headers=HEADERS)
        print(response.text)
        response.close()
    except Exception as e:
        print("Error sending data:", e)

# 🔹 Main Loop
connect_wifi()
while True:
    try:
        # Baca Sensor
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Kontrol LED
        led_red.value(1 if temperature < 35 or temperature > 60 else 0)
        led_yellow.value(1 if humidity < 40 or humidity > 60 else 0)
        
        # Kontrol Buzzer
        buzzer.value(1 if temperature < 35 or temperature > 60 or humidity < 40 or humidity > 60 else 0)
        
        # Update OLED Display
        oled.fill(0)
        oled.text("Suhu: {} C".format(temperature), 0, 10)
        oled.text("Kelembaban: {} %".format(humidity), 0, 30)
        oled.show()
        
        # Kirim Data ke Ubidots
        send_data(temperature, humidity)
        
        time.sleep(10)  # Delay sebelum iterasi berikutnya
    except OSError as e:
        print("Error Data")
        oled.fill(0)
        oled.text("Sensor Error", 20, 30)
        oled.show()
        time.sleep(2)
