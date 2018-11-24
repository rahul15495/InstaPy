import json
import codecs
import os
import random

path= "influencer_data"

def dump_user(data):

    try:
        os.stat(path)
    except:
        os.mkdir(path)
    
    with open("{}/{}.json".format(path,'influencer_bio'),'rb') as f:
        
        try:
            df= json.load(f)
        except:
            df= []
        finally:
            df.append(data)

    with open("{}/{}.json".format(path,'influencer_bio'),'wb') as f:
        
        json.dump(df,codecs.getwriter('utf-8')(f), ensure_ascii=False, default = lambda x: None)

def dump_visited(user, bulk=False):
    try:
        os.stat(path)
    except:
        os.mkdir(path)
    
    with open("{}/{}.json".format(path,'visited'),'rb') as f:
        
        try:
            df= json.load(f)
            # print(df)
        except:
            df= {}
        finally:
            if bulk:
                for u in user:
                    if u in df.keys():
                        continue
                    else:
                        df[u]= False
            else:
                df[user]= True

    with open("{}/{}.json".format(path,'visited'),'wb') as f:
        
        json.dump(df,codecs.getwriter('utf-8')(f), ensure_ascii=False, default = lambda x: None)

def hasVisited(user):
    with open("{}/{}.json".format(path,'visited'),'rb') as f:

        df= json.load(f)

        try:
            return df[user]
        except:
            False

