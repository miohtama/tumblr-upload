"""

    Upload multiple JPEGs, in given order, to Tumblr with their EXIF metadata text as the description.

"""

import sys

#from stat import S_ISREG, ST_MODE, ST_MTIME
import os
import json
from urllib2 import HTTPError

import oauth2 as oauth
from tumblr import TumblrClient
import nltk.data
from iptcinfo import IPTCInfo

# Create this file in each folder to remember the made posts
INDEX_FILENAME = "tumblr.index"

# On demand install of NLTK data
if not os.path.exists(os.path.join(os.environ["HOME"], "nltk_data")):
    nltk.download('punkt')

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

# Tumblr client instance
tumblr = None


class Index:
    """
    Keep a track file of posted photos per folder locally as
    local image file -> tumblr post id mappings.

    This way we do not post the same photo twice.
    """

    def __init__(self, path):
        """
        :param path: Path to the folder which images we track
        """
        self.path = path
        self.data = None
        self.load()

    def load(self):
        index_file = os.path.join(self.path, INDEX_FILENAME)
        if os.path.exists(index_file):
            f = open(index_file, "rt")
            data = json.load(f)
            f.close()
            self.data = data
        else:
            self.data = {}

    def save(self):
        """
        """
        index_file = os.path.join(self.path, INDEX_FILENAME)
        f = open(index_file, "wt")
        json.dump(self.data, f)
        f.close()

    def is_already_posted(self, image_path):
        """
        """
        return image_path in self.data

    def update(self, image_path, id):
        """
        """
        self.data[image_path] = id


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
    try:
        info = IPTCInfo(path)
        title = os.path.basename(path)
        desc = info.data['caption/abstract']
    except:
        desc = False

    if not desc:
        # No metadata
        title = os.path.basename(path)
        description = ""
        return title, description

    # Picasa guys screwed it up
    # https://groups.google.com/forum/?fromgroups=#!topic/picasawebalbums/CjeRCs402WA

    desc = desc.decode("utf-8")

    return title, desc

    # Split desc to title and description using natural language processing
    # http://stackoverflow.com/a/4576110/315168
    # sentences = tokenizer.tokenize(desc)

    # for s in sentences:
    #     print s.encode("utf-8")

    # if len(sentences) >= 2:
    #     return sentences[0], desc
    # else:
    #     return sentences[0], ""


def main():

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
    dirpath = sys.argv[1] if len(sys.argv) >= 2 else r'.'

    # Read extra photo description injection (the name of the place) from command line
    if len(sys.argv) > 2:
        description_prefix = sys.argv[2].decode("utf-8")
    else:
        description_prefix = None

    if len(sys.argv) > 3:
        tags = sys.argv[3]
    else:
        tags = None

    index = Index(dirpath)

    # get all entries in the directory w/ stats
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)
    entries = list(entries)
    
    # For sorting keys see os.stat https://docs.python.org/2/library/os.html#os.stat
    for stats, path in sorted(entries, key=lambda entry: entry[0].st_mtime):
        root, ext = os.path.splitext(path)
        if ext.lower() not in [".jpg", ".jpeg"]:
            # Only consider images
            continue

        # XXX: Currently Tumblr does not have separate title and description
        # for photos.. only for text posts
        title, desc = get_photo_title_and_description(path)

        if description_prefix:
            desc = u"<em>%s.</em> %s" % (description_prefix, desc)

        if not index.is_already_posted(path):
            print "Posting %s: %s" % (path.encode("utf-8"), desc.encode("utf-8"))
            try:
                response = tumblr.create_photo_post(path, request_params={"caption": desc, "tags": tags})
            except HTTPError, e:
                # Some verbosity what the fusck is going on
                # Usually '{"meta":{"status":400,"msg":"Bad Request"},"response":{"errors":["Oh no! You\'ve reached your photo upload limit for today. Please come again tomorrow!"]}}'
                print e.read()
                raise e

            response = json.loads(response)
            if response["meta"]["status"] != 201:
                print response
                raise RuntimeError("Tumbrl unsuccesful")

            tumblr_id = response["response"]["id"]
            index.update(path, tumblr_id)
            index.save()
        else:
            print "Already posted %s" % path.encode("utf-8")


if __name__ == "__main__":
    main()
