# kidde-homesafe
A slim python wrapper of the Kidde HomeSafe private API. If you're new to python, poke around [the code][kidde_homesafe.py]; it's simple, and you may understand more than you expect.

# Basic Usage
## Importing and asyncio
The following code snippets assume you have imported the following:
```python
from kidde_homesafe import KiddeClient, KiddeCommand
import asyncio
import json
```
They should be run in an asyncio loop, like this (see [asyncio][asyncio] for details):
```python
async def main() -> None:
    # Kidde functions

if __name__ == "__main__":
    asyncio.run(main())
```
## Login
Use the `from_login` class method to create your first client:
```python
client = await KiddeClient.from_login("test@example.com", "KiddeCloudPassword")
```
## Reuse Cookies
You may save a client's cookies to a file:
```python
with open("kidde_cookies.json", "w") as file:
    json.dump(client.cookies, file)
```
And reuse them later:
```python
with open("kidde_cookies.json") as file:
    cookies = json.load(file)
client = KiddeClient(cookies)
```
## Get Data
`client.get_data` returns a `KiddeDataset` object with `locations`, `devices`, and `events`. You can skip pulling `devices` with the `get_devices=False` parameter and the same with `events`. For example,
```python
dataset = await client.get_data(get_events=False)
print(dataset.devices)
```
should print something like:
```json
{
    "918281": {
        "id": 918281,
        "serial_number": "00123456789Z",
        "model": "wifidetector",
        "notify": true,
        "location_id": 018271,
        "label": "Kithen",
        "lost": false,
        "hwrev": "WD-ESP32",
        "ptt_state": "idle",
        "locate_active": false,
        "instance_id": "29ba9019ca",
        "notify_contact": true,
        "last_test_time": "2023-11-10T18:56:02Z",
        "motion_active": false,
        "weather_active": false,
        "capabilities": [
            "smoke",
            "co"
        ],
        "errors": [],
        "smoke_alarm": false,
        "co_alarm": false,
        "smoke_level": 0,
        "smoke_comp": -5,
        "too_much_smoke": false,
        "smoke_hushed": false,
        "co_level": 0,
        "fwrev": {
            "wm": "2.5",
            "net": "4.4.1",
            "alarm": "1.10"
        },
        "life": 535,
        "batt_volt": 0,
        "battery_state": "ok",
        "ptt_active": false,
        "identifying": false,
        "announcement": "Kitchen",
        "notify_eol": true,
        "diag_params": {
            "ap_rssi": -47
        },
        "mb_model": 39,
        "last_seen": "2023-11-10T18:59:02.932375951Z",
        "ssid": "YourHomeWiFi",
        "ap_rssi": -47,
        "country_code": "US",
        "longitude": 0,
        "latitude": 0,
        "altitude": 0,
        "accuracy": 0,
        "end_of_life_status": 1
    }
}
```
## Sending Device Commands
You can send API commands to your device using the KiddeCommand enum:
```python
await client.device_command(location_id=018271, device_id=918281, KiddeCommand.IDENTIFY)
```
IDENTIFY is labeled "ping" in the app.

[asyncio]: https://docs.python.org/3/library/asyncio.html
