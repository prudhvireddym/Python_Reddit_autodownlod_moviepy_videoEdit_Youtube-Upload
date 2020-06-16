import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib.request
from urllib.error import HTTPError
import requests
import glob
import schedule
from moviepy.editor import *
from moviepy.editor import VideoFileClip, concatenate_videoclips
import moviepy.editor as mp
import subprocess
import datetime

import http.client
import httplib2
import random
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

posts = []
postid = []
postname = []
username = []
videos = []
required_posts = True
global url

directory = r'D:\\Reddit\\WatchPeopleDieInside'
watermarkDir = r"D:\\Reddit\\watermark"




########################################################## Youtube Variables #################################################################


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "clients_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


##############################################Youtube Code################################################################


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options, url, subreddit):
    tags = None
    options.keywords = "reddit,watchpropledieinside,funny,bestofreddit,dailyreddit,daily reddit."
    if options.keywords:
        tags = options.keywords.split(",")
    if url == "https://www.reddit.com/r/" + subreddit + "/top/?t=month":
        vid_title = "WATCH PEOPLE DIE INSIDE Best Of The Month"
    elif url == "https://www.reddit.com/r/" + subreddit + "/top/?t=day":
        vid_title = "WATCH PEOPLE DIE INSIDE - Reddit r/watchpeopledieinside"
    elif url == "https://www.reddit.com/r/" + subreddit + "/top/?t=week":
        vid_title = "WATCH PEOPLE DIE INSIDE Best Of The Week"

    body = dict(
        snippet=dict(
            title= vid_title,
            description="This is the best curated content from the subreddit  r/watch people die inside. enjoy please like, comment and subscribe for more",
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(list(body.keys())),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload("D:\\Reddit\\watermark\\output.mp4", chunksize=-1,
                                   resumable=True)
    )

    resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(("Video id '%s' was successfully uploaded." % response['id']))
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(("Sleeping %f seconds and then retrying...", sleep_seconds))
            time.sleep(sleep_seconds)


def youtubemain(url, subreddit):
    print('youtube main running')
    argparser.add_argument("--file", help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description",
                           default="Test Description")
    argparser.add_argument("--category", default="22",
                           help="Numeric video category. " +
                                "See keywords")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
                           default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                           default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()

    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args, url, subreddit)
    except HttpError as e:
        print(("An HTTP error %d occurred:\n%s" + (e.resp.status, e.content)))


def download_file(url, idx, ):
    # local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    completeName = os.path.join('D:\\Reddit\\WatchPeopleDieInside',
                                username[idx].split('/')[-2] + "_" + postname[idx] + ".mp4")
    # completename = username[idx].split('/')[-2] + "_" + postname[idx] +".mp4"
    r = requests.get(url, stream=True)
    with open(completeName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian'''
    #urllib.request.urlretrieve(url, completeName)


def gen_output(url, subreddit):
    if not os.path.exists('D:\\Reddit\\output.mp4'):
        print('output file does not exist')
        transfilepath = ('D:\\Reddit\\transition.mp4')
        intro = ('D:\\Reddit\\intro.mp4')
        outro = ('D:\\Reddit\\outro.mp4')
        no_of_vids = len(
            [name for name in os.listdir(watermarkDir) if os.path.isfile(os.path.join(watermarkDir, name))])
        print(no_of_vids)
        for file in os.listdir(watermarkDir):
            if file.endswith(".mp4"):
                filePath = os.path.join('D:\\Reddit\\watermark', file)
                print(filePath)
                video = VideoFileClip(filePath)
                w, h = video.size  # size of the clip
                print("width and height: " + str(w) + " " + str(h))
                if h != 1080:
                    video = video.resize(height=1080)
                videos.append(video)
                print("Normal video appended")

        for vid in range(0, no_of_vids):
            print(vid)
            print("rem 2 =", vid % 2)
            if (vid % 2 == 1):
                video = VideoFileClip(transfilepath)
                w, h = video.size  # size of the clip
                if h != 1080:
                    video = video.resize(height=1080)
                if w >= 1000:
                    video = video.resize(width=1920)
                videos.insert(vid, video)
                print("Trans video Inserted")

        video = VideoFileClip(intro)
        w, h = video.size  # size of the clip
        if h != 1080:
            video = video.resize(height=1080)
        if w >= 1000:
            video = video.resize(width=1920)
        videos.insert(0, video)

        video = VideoFileClip(outro)
        w, h = video.size  # size of the clip
        if h != 1080:
            video = video.resize(height=1080)
        if w >= 1000:
            video = video.resize(width=1920)
        videos.insert(len(videos), video)

        print(videos)
        final_clip = concatenate_videoclips(videos, method="compose")
        final_clip.to_videofile(os.path.join('D:\\Reddit\\watermark', "output.mp4"), fps=60,
                                remove_temp=False)


def watermark(url, subreddit):
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            username = filename.split("_")[0]
            name = os.path.join(directory, filename)
            print("Name:", name, "Username:", username)
            my_clip = VideoFileClip(name,audio=True)  # The video file with audio enabled
            w, h = my_clip.size  # size of the clip
            print("width and height: " + str(w) + " " + str(h))

            # A CLIP WITH A TEXT AND A BLACK SEMI-OPAQUE BACKGROUND

            txt = TextClip("u/" + username, font='Arial',
                           color='white', fontsize=30)

            txt_col = txt.on_color(size=(my_clip.w + txt.w, txt.h),
                                   color=(0, 0, 0), pos=(6, 'center'), col_opacity=0.4)

            # This example demonstrates a moving text effect where the position is a function of time(t, in seconds).
            # You can fix the position of the text manually, of course. Remember, you can use strings,
            # like 'top', 'left' to specify the position
            txt_mov = txt_col.set_pos(lambda t: (max(w / 30, int(w - 0.5 * w * t)),
                                                 max(5 * h / 6, int(100 * t))))

            # Write the file to disk
            final = CompositeVideoClip([my_clip, txt_mov])
            final.duration = my_clip.duration
            final.write_videofile(os.path.join('D:\\Reddit\\watermark', username + ".mp4"), fps=60,
                                  codec='libx264')

    gen_output(url, subreddit)


def scrap_down_vids(url, subreddit):
    browser = webdriver.Firefox(executable_path=r'geckodriver.exe')
    browser.get(url)
    time.sleep(1)
    elem = browser.find_element_by_tag_name("body")
    no_of_pagedowns = True
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        for a in browser.find_elements_by_xpath('.//a'):
            if a.get_attribute('href'):
                # print(a.get_attribute('href'))
                link = a.get_attribute('href')
                if "comments" in link and link not in posts and "instanceId" not in link:
                    posts.append(link)
                    print(len(posts))
                    if (len(posts) == 12):
                        no_of_pagedowns = False
                        break
    for idx, post in enumerate(posts):
        counter = 0
        print(post)
        idn = post.split('/')[6]
        postid.insert(idx, idn)
        print("idx counter:", idx)
        print("The Post ID is:", postid[idx])
        idna = post.split('/')[7]
        postname.append(idna)
        print("The Post name is:", postname[idx])
        browser.get(post)
        time.sleep(2)
        elems = browser.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            usernamelink = elem.get_attribute('href')
            if "user" in usernamelink and usernamelink not in username:
                if (counter == 0):
                    print("The username is:", usernamelink)
                    username.append(usernamelink)
                    counter = 1
        browser.get("https://lew.la/reddit/")
        input_field = browser.find_element_by_id("url-input")
        input_field.send_keys(post)
        browser.find_element_by_class_name("download-button").click()
        time.sleep(4)
        browser.get('https://lew.la/reddit/clips/' + postid[idx] + '.mp4')
        time.sleep(4)
        download_file('https://lew.la/reddit/clips/' + postid[idx] + '.mp4', idx)
    browser.close()



if __name__ == '__main__':
    argparser.add_argument("--url", required=False, help="Time")
    argparser.add_argument("--subreddit", required=False, help="Subreddit name")
    argparser.add_argument("--now", required=False, help="Subreddit name")
    arg = argparser.parse_args()
    strt_time = "17:38"
    if arg.url and arg.subreddit:
        url = arg.url
        subreddit = arg.subreddit
        print("arg URL:" + arg.url)
    else:
        exit("Enter the argument --day/month/week")
    if url == "day":
        url = "https://www.reddit.com/r/" + subreddit + "/top/?t=day"
    elif url == "week":
        url = "https://www.reddit.com/r/" + subreddit + "/top/?t=week"
    elif url == "month":
        url = "https://www.reddit.com/r/" + subreddit + "/top/?t=month"
    print(url)

    def all_tasks():
        if not os.listdir(directory):
            print("Main directory is empty")
            scrap_down_vids(url, subreddit)
        if not os.listdir(watermarkDir):
            print("Watermark Directory is  empty")
            watermark(url, subreddit)
        if not os.path.exists('D:\\Reddit\\watermark\\output.mp4'):
            print("Output File does not exist")
            gen_output(url,subreddit)
            youtubemain(url, subreddit)
            for root, dirs, files in os.walk(directory):
                for file in files:
                    os.remove(os.path.join(root, file))
            for root, dirs, files in os.walk(watermarkDir):
                for file in files:
                    os.remove(os.path.join(root, file))
        else:
            print("Output File exists")
            youtubemain(url, subreddit)
            for root, dirs, files in os.walk(directory):
                for file in files:
                    os.remove(os.path.join(root, file))
            for root, dirs, files in os.walk(watermarkDir):
                for file in files:
                    os.remove(os.path.join(root, file))

    if(arg.now == "1"):
        all_tasks()
    schedule.every().day.at(strt_time).do(all_tasks)

    while True:
        schedule.run_pending()
        time.sleep(60)
        print("Time Now:",datetime.datetime.now(),"Waiting till:",strt_time)


