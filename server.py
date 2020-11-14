import os
from flask import Flask, request, make_response
import pprint
import hashlib
from semver import VersionInfo

app = Flask(__name__)

# 'HTTP_USER_AGENT': 'ESP8266-http-Update',
#  'HTTP_X_ESP8266_AP_MAC': '42:F5:20:2D:3A:10',
#  'HTTP_X_ESP8266_CHIP_ID': '2963984',
#  'HTTP_X_ESP8266_CHIP_SIZE': '4194304',
#  'HTTP_X_ESP8266_FREE_SPACE': '2822144',
#  'HTTP_X_ESP8266_MODE': 'spiffs',
#  'HTTP_X_ESP8266_SDK_VERSION': '2.2.2-dev(38a443e)',
#  'HTTP_X_ESP8266_SKETCH_MD5': '86b0bec02dbe51265614f329592e2362',
#  'HTTP_X_ESP8266_SKETCH_SIZE': '321040',
#  'HTTP_X_ESP8266_STA_MAC': '40:F5:20:2D:3A:10',
#  'HTTP_X_ESP8266_VERSION': 'v0.1.0',

fw_set = set()
for root, dirs, files in os.walk("firmware/"):
    for file in files:
        try:
            r, _ = os.path.splitext(file)
            v = VersionInfo.parse(r)
            fw_set.add((v, os.path.join(root, file)))
        except ValueError:
            print(file)
            pass

fw_v, fw_path = max(fw_set)
print(fw_v)
print(fw_path)

def get_bin():
    with open(fw_path, "rb") as fp:
        return fp.read()

@app.route('/')
def index():

    pprint.pprint(request.environ)

    if request.environ["HTTP_USER_AGENT"] != "ESP8266-http-Update":
        return ('', 403)

    current = request.environ["HTTP_X_ESP8266_VERSION"].lstrip("v")
    try:
        current = VersionInfo.parse(current)
    except ValueError:
        return (f"{current} is an invalid version string", 400)

    if current < fw_v:
        fw = get_bin()
        resp = make_response(fw, 200)
        resp.headers["Content-Type"] = "application/octet-stream"
        resp.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(fw_path)}"
        resp.headers["Content-Length"] = len(fw)
        resp.headers["x-MD5"] = hashlib.md5(fw).hexdigest()
        return resp


    return ('', 304)
