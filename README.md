# An appdaemon script for Home Assistant, to monitor and alert for price changes on the amazon shopping marketplace.

Note: Requires requests and bs4 to be added to the required python packages
```
python_packages:
    - bs4
    - requests
```

Config:<br/>
```
apt:
  module: apt
  class: APT
  items:
    - name: <Item friendly name>
      url: "Full amazon.com link"
      below_threshold: Price to trigger the binary sensor when it drops below
```
