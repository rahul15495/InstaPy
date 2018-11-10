import sys
import time
import os
import subprocess
import json
from logger import *
import traceback
import messenger

watchdir = '/home/ec2-user/iPROCESS/S3/test/'
paramsdir = '/home/ec2-user/iPROCESS/S3/params/'
#watchdir = '/var/www/html/pending/'
#paramsdir = '/var/www/html/params/'

pending_contents = os.listdir(watchdir)
params_contents = os.listdir(watchdir)
count = len(watchdir)
dirmtime = os.stat(watchdir).st_mtime

########### pq config #####################

queues= messenger.generate_qs()
channel= messenger.config_channel()
messenger.create_queues(queues, channel) 

#############################################


while True:
    newmtime = os.stat(watchdir).st_mtime
    if newmtime != dirmtime:
        dirmtime = newmtime

        new_pending_contents = os.listdir(watchdir)
        new_params_contents = os.listdir(watchdir)
        pending_added = set(new_pending_contents).difference(pending_contents)
        params_added = set(new_params_contents).difference(params_contents)

        if pending_added:
            logging.debug(
                "**************************************************************")
            logging.debug("Files added: %s" % (" ".join(pending_added)))
            for file in pending_added:
                try:
                    logging.debug('file name :: {}'.format(file))
                    _file = ".".join(file.split('.')[:-1])
                    with open("/home/ec2-user/iPROCESS/S3/params/Sample_1_IMG_ID_20180802_114312_537_2_763582/Sample_1_IMG_ID_20180802_114312_537_2_763582.json") as f:
                        df = json.load(f)
                        df[0]['ImageName']= watchdir+file
                        produce = df[0]['Produce']
                        name = file
                        try:
                            # subprocess.call(["python3",
                            #                  os.environ['HOME'] +
                            #                  '/iPROCESS/python_scripts/api.py',
                            #                  watchdir+name,
                            #                  '0',
                            #                  lic_type,
                            #                  produce,
                            #                  variety,
                            #                  uniqueID,
                            #                  sizeBucket,
                            #                  callbackURL,
                            #                  RangeType,
                            #                  Customer_id])

                            channel= messenger.config_channel()


                            messenger.send_msg( json.dumps(df),
                                                channel,
                                                '{}_key'.format(produce.lower()),
                                                1
                                             )

                        except:
                            traceback.print_exc()
                            logging.debug(traceback.format_exc())
                            logging.debug(
                                'failed running python script: iPROCESS.py')
                except:
                    logging.debug(traceback.format_exc())
                    logging.debug('failed reading :'+paramsdir +
                                  _file+'/'+_file+'.json')

        continue

        pending_contents = new_pending_contents
        params_contents = new_params_contents
    time.sleep(1)
