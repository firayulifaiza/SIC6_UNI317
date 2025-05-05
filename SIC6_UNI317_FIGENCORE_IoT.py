from machine import Pin, I2C
import ssd1306
import time
import dht
import network
import urequests

# 🔹 Konfigurasi WiFi
SSID = "haechanahcheah"
PASSWORD = "sary1234"

# 🔹 Konfigurasi API Ubidots
UBIDOTS_TOKEN = "BBUS-DRfFDUMilSnfdNoymtMcL741UKEUD"
UBIDOTS_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/IOT_ESP32_UNI317/"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# 🔹 Konfigurasi API Flask
FLASK_URL = "http://192.168.208.118:8000/data"  # URL Flask endpoint
FLASK_HEADERS = {
    "Content-Type": "application/json"
}

# 🔹 Koneksi WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())

# 🔹 Setup I2C untuk OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# 🔹 Setup Sensor DHT22
dht_sensor = dht.DHT22(Pin(4))  # DHT22 di GPIO4

# 🔹 Setup LED dan Buzzer
led_red = Pin(18, Pin.OUT)      # LED merah di GPIO18
led_yellow = Pin(15, Pin.OUT)   # LED kuning di GPIO15
buzzer = Pin(2, Pin.OUT)        # Buzzer di GPIO2

# 🔹 Kirim Data ke Ubidots
def send_data(temp, hum):
    data = {
        "suhu_kompos": temp,
        "kelembaban_kompos": hum
    }
    try:
        response = urequests.post(UBIDOTS_URL, json=data, headers=HEADERS)
        if response.status_code == 201:
            print("Data berhasil dikirim ke Ubidots.")
        else:
            print("Gagal mengirim data:", response.status_code)
        response.close()
    except Exception as e:
        print("Error sending data:", e)
    
# 🔹 Kirim Data ke Flask
def send_data_to_flask(temp, hum):
    data = {
        "temperature": temp,
        "humidity": hum
    }
    try:
        payload = json.dumps(data)
        response = urequests.post(FLASK_URL, data=payload, headers=FLASK_HEADERS)
        if response.status_code == 200 or response.status_code == 201:
            print("Data successfully sent to Flask.")
        else:
            print(f"Failed to send data to Flask: {response.status_code}")
        response.close()
    except Exception as e:
        print("Error sending data to Flask:", e)

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
        
        # Kirim Data ke Ubidots jika WiFi aktif
        if network.WLAN(network.STA_IF).isconnected():
            send_data(temperature, humidity)
        else:
            print("WiFi tidak terhubung.")

        time.sleep(10)  # Delay sebelum iterasi berikutnya
    except OSError as e:
        print("Error Data")
        oled.fill(0)
        oled.text("Sensor Error", 20, 30)
        oled.show()
        time.sleep(2)
