"""

    Upload multiple JPEGs, in given order, to Tumblr with their EXIF metadata text as the description.

"""

import sys
from stat import S_ISREG, ST_MODE, ST_MTIME
import os

import oauth2 as oauth
from tumblr import TumblrClient
import nltk.data
from iptcinfo import IPTCInfo

# On demand install of NLTK data
if not os.path.exists(os.path.join(os.environ["HOME"], "nltk_data")):
    nltk.download('punkt')

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

# Tumblr client instance
tumblr = None


def get_photo_title_and_description(path):
    """
    Extract JPEG metadata and parse title and description out of it.
    Images *must* be edited with Picasa.

    Use the first sentence of the description as a title.

    Handle wacky cases like usage of ... and ""

    Looks like Picasa does not use standard EXIF
    metadata http://productforums.google.com/forum/#!topic/picasa/fiNTD6432as
    but IPTC instead.


    """
    info = IPTCInfo(path)

    desc = info.data['caption/abstract']

    if not desc:
        # No metadata
        title = os.path.basename(path)
        description = ""
        return title, description

    # Picasa guys screwed it up
    # https://groups.google.com/forum/?fromgroups=#!topic/picasawebalbums/CjeRCs402WA

    desc = desc.decode("utf-8")

    # http://stackoverflow.com/a/4576110/315168
    sentences = tokenizer.tokenize(desc)

    for s in sentences:
        print s.encode("utf-8")

    if len(sentences) >= 2:
        return sentences[0], desc
    else:
        return sentences[0], ""


def spoof_url(path):
    """
    Create unique URL id for posts based on filename
    """
    return "file://" + os.path.basename(path)


def post_photo(description, path):
    """
    We use filename as source URL that we get a proper unique id
    to avoid double posting.
    """
    photo = open(path, 'rb')
    tumblr.post('post',
        blog_url=os.environ["BLOG"],
        params={'type': 'photo',
                'caption': description,
                'data': photo,
                'source': spoof_url(path)})


def lister(client, count, params={}):
    client.get_blog_posts()

    total = 0
    while True:
        print "making a request"
        params['offset'] = total
        json_response = client.get_blog_posts(request_params=params)
        print json_response
        if not json_response:
            break

        if len(json_response['response']['posts']) == 0:
            raise StopIteration

        for post in json_response['response']['posts']:
            total += 1
            if total > count:
                raise StopIteration
            yield post

# http://stackoverflow.com/a/539024/315168
if not os.environ.get("KEY", None):
    sys.exit("Give app key as KEY env")

if not os.environ.get("SECRET", None):
    sys.exit("Give app key as SECRET env")


if not os.environ.get("TOKEN", None):
    sys.exit("Give Oauth token as TOKEN env")

if not os.environ.get("VERIFIER", None):
    sys.exit("Give Oauth verifier as VERIFIER env")

if not os.environ.get("BLOG", None):
    sys.exit("Give blog URL as BLOG env")

# Create Tumblr client

consumer = oauth.Consumer(os.environ["KEY"], os.environ["SECRET"])
token = oauth.Token(os.environ["TOKEN"], os.environ["VERIFIER"])

tumblr = TumblrClient(os.environ["BLOG"], consumer, token)

# path to the directory (relative or absolute)
dirpath = sys.argv[1] if len(sys.argv) == 2 else r'.'

# get all entries in the directory w/ stats
entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
entries = ((os.stat(path), path) for path in entries)

# leave only regular files, insert creation date
entries = ((stat[ST_MTIME], path)
           for stat, path in entries if S_ISREG(stat[ST_MODE]))
#NOTE: on Windows `ST_CTIME` is a creation date
#  but on Unix it could be something else
#NOTE: use `ST_MTIME` to sort by a modification date

for mdate, path in sorted(entries):
    root, ext = os.path.splitext(path)
    if ext.lower() not in [".jpg", ".jpeg"]:
        # Only consider images
        continue

    # XXX: Currently Tumblr does not have separate title and description
    # for photos.. only for text posts
    title, desc = get_photo_title_and_description(path)
    #response = tumblr.create_post(request_params={"type": "text", "body": "foobar"})
    response = tumblr.create_photo_post(path, request_params={"caption": desc})
    print response
    break

for post in lister(tumblr, 10, params={'type': 'photo'}):
    print post['id']


