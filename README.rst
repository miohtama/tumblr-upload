.. contents:: :local:

Introduction
----------------

Mass upload a folder of photos as Tumblr posts. Give it a folder and it will create Tumblr posts
from the photos. The same photo is not uploaded twice.

Use JPEG EXIF and IPTC (Google Picasa) metadata description as post title or post description.
It uses `Natural Language Toolkit <http://www.nltk.org/>`_ for extracting sentences and stuff.


Installation
--------------


Install::

    git clone git://github.com/miohtama/tumblr-upload.git
    cd tumbrl-upload
    virtualenv venv
    . venv/bin/activate
    easy_install oauth2 nltk poster
    pip install https://github.com/miohtama/tumblr-python/tarball/master

Login to Tumblr.

Register an application at:

    http://www.tumblr.com/oauth/apps

Make dummy title and set "xxx" as the default callback URL on
the app creation page.

Get OAuth key and secret for your application on your Apps setting page.

Authorize the command line client to work against your blog using the app credentials::

   BLOG=onewaytickettobrazil.tumblr.com KEY=xxx SECRET=yyy python authorize.py

Go to given URL. Click *Allow*.

Pick up the ouath_token and ouath_verifier from the resulting browser address
bar and give it the script asking for it::

    http://www.tumblr.com/oauth/None?oauth_token=yyy&oauth_verifier=aaa

Now ``authorize.py`` generates upload.sh script which has your Tumbrl
credentials stored permanently.

Usage
--------------

You call the script with arguments:

    upload.sh [folder] [prefix text] [tags]

Where

* *folder* is the folder of which all files will be uploaded. Duplicate uploads are avoided by using a tracking file

* *prefix text* is inserted at the beginning of each photo description

* *tags* is a comma separated list of Tumblr tags you want to assing on the photo

After installation you can upload a folderful of photos::

    ./upload.sh ~/Desktop/sushinight/Sao\ Paulo\ highlights\ 2/

You can also add some prefix text to all photo captions::

    ./upload.sh ~/Desktop/sushinight/copacabana "RIO DE JANEIRO"

And then with tags::

    ./upload.sh ~/Desktop/sushinight/copacabana "RIO DE JANEIRO" "brazil, riodejaneiro"

Troubleshooting
------------------

If you get 401 responses from Tumblr OAuth API your clock might be wrong time and
timestamp check fails.

Links
-------

* https://github.com/medecau/tumblr-python

* https://gist.github.com/1242662

* http://www.tumblr.com/docs/en/api/v2#posting
