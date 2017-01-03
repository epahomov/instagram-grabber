import json
import logging
import os
import urllib
import urllib2
import archive

base_dir = "/Users/egor/downloaded_photos/instagram/"

logging.basicConfig(filename= base_dir + "logging",format='%(asctime)s %(message)s',level=logging.DEBUG)

images_dir = base_dir + "images/"

processed_users = set(map(lambda x: x.split("\n")[0], open(base_dir + "processed_users", "r").readlines()))
users_to_process = map(lambda x: x.split("\n")[0], open(base_dir + "users_to_process", "r").readlines())

total_number_of_downloaded_images = len(os.listdir(images_dir)) / 2

logging.info("Starting script. Number of unarchived images = " + str(total_number_of_downloaded_images))

for user_to_process in users_to_process:
    if user_to_process not in processed_users:
        try:
            processed_users.add(user_to_process)
            add_processed_user = open(base_dir + "processed_users", "a")
            add_processed_user.write(user_to_process + '\n')
            add_processed_user.close()

            account = user_to_process
            logging.info("Processing " + account)
            account_url = "https://www.instagram.com/" + account + "/"

            r = filter(lambda x: "sharedData" in x, urllib2.urlopen(account_url).read().split("\n"))

            script_data = json.loads(r[0][52:][:-10])
            csrf = script_data["config"]["csrf_token"]
            user = script_data["entry_data"]["ProfilePage"][0]["user"]
            id = user["id"]

            url = "https://www.instagram.com/query/"

            values = {"q": """ig_user(""" + id + """) { media.after(0, 1000) {
                         count,
                         nodes {
                           caption,
                           code,
                           comments {
                             count
                           },
                           comments_disabled,
                           date,
                           dimensions {
                             height,
                             width
                           },
                           display_src,
                           id,
                           is_video,
                           likes {
                             count
                           },
                           owner {
                             id
                           },
                           thumbnail_src,
                           video_views
                         },
                         page_info
                       }
                        }"""
                , "ref": "users::show"}

            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            opener = urllib2.build_opener()
            opener.addheaders = [  # ('Host', 'www.instagram.com'),
                # ('User-Agent', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:44.0) Gecko/20100101 Firefox/44.0"),
                # ('Accept', "*/*"),
                # ('Accept-Language', "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"),
                ('X-CSRFToken', csrf),
                # ('X-Instagram-AJAX', "1"),
                # ('Content-Type', "application/x-www-form-urlencoded"),
                # ('X-Requested-With', "XMLHttpRequest"),
                ('Referer', "https://www.instagram.com/natgeo/"),
                # ('Conten-Length', "508"),
                ('Cookie', "csrftoken=" + csrf + ";"),
                # ('Cookie', "csrftoken=91fd1bae6a77d2a45cf570d1c222030c; mid=VmtNVQAEAAGvs24GytmKeDHWDcMR; sessionid=IGSCa12526c96da8e252c371ebf805c5710da88ee776aa2986e3bd09820241e36e77%3Awe05i7Ak24DZ0MtkpWaEG2p5BJnId0dk%3A%7B%22asns%22%3A%7B%2273.241.151.59%22%3A7922%2C%22time%22%3A1471926976%7D%7D; s_network=; ig_pr=0.6666666865348816; ig_vw=3840"),
                # ('Connection', "keep-alive")
            ]

            response = opener.open(req)
            result = response.read()

            followed_by = user["followed_by"]["count"]
            logging.info(account + " followed by " + str(followed_by))
            count_of_images = 0
            for x in json.loads(result)["media"]["nodes"]:
                try:
                    if not x["is_video"] and x["date"] > 1420074061:
                        count_of_images += 1
                        total_number_of_downloaded_images += 1
                        if (total_number_of_downloaded_images % 100 == 0):
                            logging.info("Downloaded " + str(total_number_of_downloaded_images))
                        if (total_number_of_downloaded_images > 1000000):
                            logging.info("Archiving!")
                            archive.archive_directory(dir_to_archive=images_dir,
                                                      file_with_all_metadata=base_dir + "all_metadata",
                                                      destination_dir=base_dir)
                            total_number_of_downloaded_images = 0
                            logging.info("Done archiving!")
                        code = x["code"]
                        urllib.urlretrieve(x["thumbnail_src"], images_dir + code + ".jpg")
                        meta_info = open(images_dir + code + ".txt", "w")
                        json.dump(x, meta_info)
                        meta_info.write("\n" + account + "\n" + id + "\n" + str(followed_by))
                        meta_info.close()
                except Exception as e:
                    logging.error("Could not process " + x)
            logging.info("done with " + account + ". count of images " + str(count_of_images))
        except Exception as e:
            logging.error("Could not process account " + user_to_process)


