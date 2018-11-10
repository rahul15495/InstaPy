import messenger
from logger import *
import api
import json
import traceback


def callback(ch, method, properties, body):
    temp = body.decode('utf-8')
    df = json.loads(temp)

    file= df[0]['ImageName']
    uniqueID = df[0]['UniqueID']
    lic_type = df[0]['License']
    produce = df[0]['Produce']
    variety = df[0]['Variety']
    callbackURL = df[0]['CallBack']
    sizeBucket = df[0]['Size_info']
    RangeType = df[0]['RangeType']
    try:
        Customer_id = df[0]['Customer_id']
    except:
        Customer_id = "default"

    logging.debug("**************************************************************")
    logging.debug("^^^^^^^^^^^^^^^^json details^^^^^^^^^^")
    logging.debug('received file : {}'.format(file))
    logging.debug('uniqueID : {}'.format(uniqueID))
    logging.debug('lic_type: {}'.format(lic_type))
    logging.debug('produce: {}'.format(produce))
    logging.debug('variety {}'.format(variety))
    logging.debug('callbackURL {}'.format(callbackURL))
    logging.debug('sizeBucket {}'.format(sizeBucket))
    logging.debug('RangeType {}'.format(RangeType))

    try:

        api.process_image([ None,  #empty element to match the interface
                            file,
                            '0',
                            lic_type,
                            produce,
                            variety,
                            uniqueID,
                            sizeBucket,
                            callbackURL,
                            RangeType,
                            Customer_id])
    
    except:
        traceback.print_exc()
        logging.debug(traceback.format_exc())
        logging.debug('failed running python script: api.py')


    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # to be entered manually by the admin for each of the queues defined below.
    queue_index = 0

    queues = messenger.generate_qs()

    #########################################################################
    # [{'name': 'potato', 'routing_key': 'potato_key'},                                              │
    # {'name': 'rice_turmeric', 'routing_key': 'rice_turmeric_key'}]
    #########################################################################

    channel = messenger.config_channel()
    messenger.create_queues(queues, channel)

    messenger.consume(queues[queue_index]['name'], callback, channel)


if __name__ == '__main__':
    main()
