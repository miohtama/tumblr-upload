Mass upload a folder of photos as Tumblr posts. Give it a folder and it will create Tumblr posts
from the photos. The same photo is not uploaded twice.

Use JPEG EXIF metadata description as post title or post description.
It uses `Natural Language Toolkit <http://www.nltk.org/>`_ for extracting sentences and stuff.


Usage::

    git clone ...
    cd tumbrl-upload
    virtualenv venv
    . venv/bin/activate
    easy_install oauth2 tumblr2 nltk poster

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

Now you can upload a folderful of photos::

    ./upload.sh ~/Desktop/sushinight/Sao\ Paulo\ highlights\ 2/

Links
-------

* https://github.com/medecau/tumblr-python