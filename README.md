# An appdaemon script for Home Assistant, to monitor and alert for price changes on the amazon shopping marketplace.

Note: Requires requests and bs4 to be added to the required python packages
```
python_packages:
    - bs4
    - requests
```

For each configured item, a sensor will be created using the name value, `sensor.name_of_item`
<br/>If a below_threshold is set, a binary_sensor will be created, `binary_sensor.name_of_item_threshold`

Config:<br/>
```
apt:
  module: apt
  class: APT
  items:
    - name: <Item friendly name>
      url: "Full amazon.com link"
      below_threshold: Optional price value to trigger the binary sensor when it drops below
```
