import datetime
import requests
from bs4 import BeautifulSoup
from cleantext import clean
import hassapi as hass

class APT(hass.Hass):

    def initialize(self):
        self.items = self.args['items']
        if "notify" in self.args:
            self.notify_service = self.args['notify']
        else:
            self.notify_service = False

        self.header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"}

        self.run_in(self.get_prices, 0)
        self.run_every(self.get_prices, datetime.datetime.now(), 4800)

    def get_prices(self, kwargs):
        for chunk in self.items:
            url = chunk['url']
            name = chunk['name']
            self.log(f"Looking for {name} at {url}")
            page = requests.get(url,headers=self.header)
            if not page.ok: continue
            soup = BeautifulSoup(page.content, "html.parser")
            page.close()

            title = soup.find("span", {"id":"productTitle"})
            if title:
                title = title.get_text().lstrip()
                self.log(f"Found title {title}")
            else:
                continue
            price = soup.find("span", {"class":"a-offscreen"}).get_text().replace(',','.').replace('$','')
            entity = "sensor.apt_" + name.replace(' ', '_').lower()
            self.log(f"Setting {entity} to {price}")
            self.set_state(entity, state=price, friendly_name=title, device_class="monetary", unit_of_measurement='$')
            if "below_threshold" in chunk:
                threshold = chunk['below_threshold']
                below_threshold = "off"
                if float(price) < float(threshold):
                    below_threshold = "on"
                    binary_sensor_entity = self.get_entity("binary_" + entity + "_threshold")
                    binary_sensor_state = binary_sensor_entity.get_state()
                    if binary_sensor_state != below_threshold and self.notify_service:
                        self.log(f"The threshold {threshold} has been met for {title}. The binary_sensor is currently set to {binary_sensor_state}. Send an alert!")
                        self.notify(message=f"{title} has gone below the threshold!", name=self.notify_service)
                self.set_state("binary_" + entity + "_threshold", state=below_threshold, friendly_name=title)
