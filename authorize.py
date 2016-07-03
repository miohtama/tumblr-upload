"""

Create command line authorization token.

"""
import os
import sys
from tumblr.oauth import TumblrOAuthClient


if not os.environ.get("KEY", None):
    sys.exit("Give app key as KEY env")

if not os.environ.get("SECRET", None):
    sys.exit("Give app key as SECRET env")

if not os.environ.get("BLOG", None):
    sys.exit("Give blog URL as BLOG env")

callback = "http://example.com/callback/"

tumblr_oauth = TumblrOAuthClient(os.environ["KEY"], os.environ["SECRET"])

auth_url = tumblr_oauth.get_authorize_url()

print "Connect with Tumblr via:\n%s\nThen pick oauth_verifier from the url" % auth_url

oauth_verifier = raw_input('Verifier: ').strip()

access_token = tumblr_oauth.get_access_token(oauth_verifier)

final_oauth_token = access_token.key
final_oauth_token_secret = access_token.secret

# Genereate the upload script which has credentials stored
out = open("upload.sh", "wt")

pwd = os.getcwd()

# http://wiki.bash-hackers.org/scripting/posparams
print >> out, """#!/bin/sh
. %s/venv/bin/activate
BLOG=%s \\
KEY=%s \\
SECRET=%s \\
TOKEN=%s \\
VERIFIER=%s \\
python %s/tumblr-upload.py "$@"
""" % (pwd, os.environ["BLOG"], os.environ["KEY"], os.environ["SECRET"], final_oauth_token, final_oauth_token_secret, pwd)

out.close()

os.system("chmod u+x upload.sh")

print "Run ./upload.sh YOURFOLDER to update your tumblr"
