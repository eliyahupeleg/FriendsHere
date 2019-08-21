import json
import urllib2

info = json.loads(urllib2.urlopen("http://jsonip.com").read())
ip = info["ip"]
print ip