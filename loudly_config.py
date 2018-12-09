def getItem():
    import random
    import json

    path= "influencer_data"

    key= None
    with open("{}/{}.json".format(path,'visited'),'rb') as f:

        df= json.load(f)
        while(1):
            key= random.choice(list(df))
            if(df[key]):
                continue
            else:
                break
    
    return key


insta_username = 'abhi_154'

insta_password = 'chaurasia15'

min_followers= 10

seed= getItem()
