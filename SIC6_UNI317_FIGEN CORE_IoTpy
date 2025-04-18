from machine import Pin, I2C
import ssd1306
import time
import dht
import network
import urequests
import json

# 🔹 Konfigurasi WiFi
SSID = "Siape"
PASSWORD = "gitaaa26"

# 🔹 Konfigurasi API Ubidots
UBIDOTS_TOKEN = "BBUS-DRfFDUMilSnfdNoymtMcL741UKEUDb"
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
led_yellow = Pin(15, Pin.OUT)  # LED kuning di GPIO15
buzzer = Pin(2, Pin.OUT)  # Buzzer di GPIO2

# 🔹 Kirim Data ke Ubidots
def send_data(temp, hum):
    data = {
        "suhu_kompos": temp,
        "kelembaban_kompos": hum
    }
    try:
        payload = json.dumps(data)
        response = urequests.post(UBIDOTS_URL, data=payload, headers=HEADERS)
        if response.status_code == 200 or response.status_code == 201:
            print("Data successfully sent to Ubidots.")
        else:
            print(f"Failed to send data: {response.status_code}")
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
        
        print("Suhu:", temperature, "°C")
        print("Kelembaban:", humidity, "%")
        
        # Control LEDs based on conditions
        if temperature < 35 or temperature > 60:
            led_red.value(1)  # LED merah menyala jika suhu di luar rentang 35-60°C
        else:
            led_red.value(0)  # LED merah mati jika suhu dalam rentang 35-60°C

        if humidity < 40 or humidity > 60:
            led_yellow.value(1)  # LED kuning menyala jika kelembaban di luar rentang 40-60%
        else:
            led_yellow.value(0)  # LED kuning mati jika kelembaban dalam rentang 40-60%

        # Buzzer control: aktif jika suhu atau kelembaban tidak optimal
        if temperature < 35 or temperature > 60 or humidity < 40 or humidity > 60:
            buzzer.value(1)  # Buzzer berbunyi
        else:
            buzzer.value(0)  # Buzzer mati
            
        # Update OLED Display
        oled.fill(0)
        oled.text("Suhu: {} C".format(temperature), 0, 10)
        oled.text("Kelembaban: {} %".format(humidity), 0, 30)
        oled.show()
        
        # Kirim Data ke Ubidots
        send_data(temperature, humidity)
        
        time.sleep(10)  # Delay sebelum iterasi berikutnya
    except OSError as e:
        print("Error reading sensor data.")
        oled.fill(0)
        oled.text("Sensor Error", 20, 30)
        oled.show()
        time.sleep(2)_
