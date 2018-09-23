import os
import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException

from instapy import InstaPy

from loudly_utils import utils as loudly_utils

def get_influencer_following_handles(session,influencer):
    following_list= session.grab_following(username=influencer, amount="full", live_match=False, store_locally=False)
    loudly_utils.dump(influencer, 'following', following_list)

def main():
    insta_username = 'abhi_154'
    insta_password = 'chaurasia15'

    # set headless_browser=True if you want to run InstaPy on a server

    # set these in instapy/settings.py if you're locating the
    # library in the /usr/lib/pythonX.X/ directory:
    #   Settings.database_location = '/path/to/instapy.db'
    #   Settings.chromedriver_location = '/path/to/chromedriver'

    session = InstaPy(username=insta_username,
                    password=insta_password,
                    headless_browser=False,
                    multi_logs=True)

    try:
        session.login()

        get_influencer_following_handles(session, "_ishwari_")

    except Exception as exc:
        # if changes to IG layout, upload the file to help us locate the change
        if isinstance(exc, NoSuchElementException):
            file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
            with open(file_path, 'wb') as fp:
                fp.write(session.browser.page_source.encode('utf8'))
            print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                '*' * 70, file_path))
        # full stacktrace when raising Github issue
        raise

    finally:
        # end the bot session
        session.end()

if __name__ == '__main__':
    main()