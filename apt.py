import datetime
import requests
from bs4 import BeautifulSoup
import hassapi as hass

class AmazonItem:
    url = False
    entitiy = False
    title = False
    price = False
    threshold = False

    def set_price(self, price):
        self.price = price

    def set_entity(self, entity):
        self.entity = entity

    def set_title(self, title):
        self.title = title

    def set_url(self, url):
        self.url = url

    def set_threshold(self, threshold):
        self.threshold = threshold

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

    def check_and_send_alert(self, item):
        below_threshold = "off"
        if float(item.price) < float(item.threshold):
            below_threshold = "on"
            binary_sensor_entity = self.get_entity("binary_" + item.entity + "_threshold")
            binary_sensor_state = binary_sensor_entity.get_state()
            if binary_sensor_state != below_threshold and self.notify_service:
                data = {
                    "url": item.url,
                    "clickAction": item.url
                }
                self.log(f"The threshold {item.threshold} has been met for {item.title}. The binary_sensor is currently set to {binary_sensor_state}. Send an alert!")
                self.notify(message=f"{item.title} is on sale at {item.price}", data=data, name=self.notify_service)
        self.set_state("binary_" + item.entity + "_threshold", state=below_threshold, friendly_name=item.title)


    def find_price_in_page(self, soup):
        price = soup.find("span", {"class":"a-offscreen"}).get_text().replace(',','.').replace('$','')
        if not price.replace(".", "").isnumeric():
            price = "NA"
        return price

    def find_title_in_page(self, soup):
        title = soup.find("span", {"id":"productTitle"})
        if title:
             title = title.get_text().strip()
             self.log(f"Found title {title}")
        return title

    def get_prices(self, kwargs):
        for chunk in self.items:
            url = chunk['url']
            name = chunk['name']
            #threshold = chunk['below_threshold']
            self.log(f"Looking for {name} at {url}")
            page = requests.get(url,headers=self.header)
            if not page.ok: continue
            soup = BeautifulSoup(page.content, "html.parser")
            page.close()

            title = self.find_title_in_page(soup)
            if not title:
                continue

            price = self.find_price_in_page(soup)
            entity = "sensor.apt_" + name.replace(' ', '_').lower()
            self.log(f"Setting {entity} to {price}")
            attributes = {
                "LastUpdated":str(datetime.datetime.now()),
                "friendly_name":title,
                "unit_of_measurement": "$"
            }
            self.set_state(entity, state=price, attributes=attributes)#friendly_name=title, device_class="monetary", unit_of_measurement='$')
            if "below_threshold" in chunk and price != "NA":
                threshold = chunk['below_threshold']
                amazon_item = AmazonItem()
                amazon_item.set_price(price)
                amazon_item.set_entity(entity)
                amazon_item.set_threshold(threshold)
                amazon_item.set_url(url)
                amazon_item.set_title(title)
                self.check_and_send_alert(amazon_item)
            elif price == "NA":
                # Force binary sensor to off if no price/offer found
                self.set_state("binary_" + entity + "_threshold", state="off", friendly_name=title)
