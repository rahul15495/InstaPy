import os
import time
from tempfile import gettempdir

import loudly_config

from selenium.common.exceptions import NoSuchElementException

from instapy import InstaPy

from loudly_utils import utils as loudly_utils
from instaCrawl.util.extractor import extract_information
from instaCrawl.util.settings import Settings

import traceback

profile_queue = []


def get_influencer_following_handles(session, influencer):
    following_list = session.grab_following(
        username=influencer, amount="full", live_match=False, store_locally=False)
    # loudly_utils.dump(influencer, 'following', following_list)
    return following_list


def crwal(session, profile):

    global profile_queue
    # set headless_browser=True if you want to run InstaPy on a server

    # set these in instapy/settings.py if you're locating the
    # library in the /usr/lib/pythonX.X/ directory:
    #   Settings.database_location = '/path/to/instapy.db'
    #   Settings.chromedriver_location = '/path/to/chromedriver'



    try:

        browser = session.browser

        profile_data = extract_information(browser, profile, Settings.limit_amount)

        if profile_data['followers'] > loudly_config.min_followers:

            loudly_utils.dump_user(profile_data)

            #following_list = get_influencer_following_handles(session, profile)

            #profile_queue = profile_queue + following_list

           # loudly_utils.dump_visited(following_list, bulk=True)
        
        else:
            print('skipping {} as follower count is : {}'.format(profile,profile_data['followers']))
        

    except Exception as exc:
        # if changes to IG layout, upload the file to help us locate the change
        if isinstance(exc, NoSuchElementException):
            file_path = os.path.join(gettempdir(), '{}.html'.format(
                time.strftime('%Y%m%d-%H%M%S')))
            with open(file_path, 'wb') as fp:
                fp.write(session.browser.page_source.encode('utf8'))
            print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                '*' * 70, file_path))
        # full stacktrace when raising Github issue
        raise

    finally:
        # end the bot session
        loudly_utils.dump_visited(profile)

        return
        


if __name__ == '__main__':

    try:

        session = InstaPy(username=loudly_config.insta_username,
                        password=loudly_config.insta_password,
                        headless_browser=True,
                        multi_logs=True)

        
        session.login()

        crwal(session,loudly_config.seed)

        
        while(1):
            if len(profile_queue) > 0 :
                user = profile_queue.pop(0)

                if not loudly_utils.hasVisited(user):
                    crwal(session, user)
                else:
                    continue
            else:
                crwal(session,loudly_config.getItem())
    
    except :
        traceback.print_exc()
        session.end()