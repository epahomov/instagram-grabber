import urllib2
import urllib
import json
import itertools
import multiprocessing
import itertools
import time
import random
import string

c = 0

text_file = open("/Users/egor/downloaded_photos/instagram/users/users.txt", "a")
proxies_file = "/Users/egor/proxies/proxies"

proxy_list = map(lambda x: x.split("\n")[0], open(proxies_file, "r").readlines())

for x in proxy_list:
    print x

proxy_number = 0

def execute(request):
    result = "-1"
    while result == "-1":
        try:
            result = urllib2.urlopen(request, timeout = 5).read()
        except Exception as e:
            print e
            global proxy_number
            proxy = proxy_list[proxy_number]
            proxy_number += 1
            print "Switched proxy to " + proxy
            proxy = urllib2.ProxyHandler({'https': proxy})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
    return result


try:
    while (True):

        size = random.randint(2, 6)

        query = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

        request = urllib2.Request("https://www.instagram.com/web/search/topsearch/?context=blended&query=" + query)

        data = execute(request)

        users = json.loads(
            data)[
            "users"]
        if c > 1000000:
            text_file.close()
            break
        for u in users:
            if not (u["user"]["is_private"]):
                c += 1
                if c % 100 == 0:
                    print c
                username = u["user"]["username"]
                follower_count = str(u["user"]["follower_count"])
                text_file.write(username + " " + follower_count + "\n")

except Exception as e:
    print e
    text_file.close()
