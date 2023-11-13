import urllib, json
import urllib.request
data = json.loads(urllib.request.urlopen("http://ip.jsontest.com/").read())
print(data["ip"])