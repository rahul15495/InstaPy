import json
import codecs
import os

path= "influencer_data"

def dump(influencer,key, data):

    try:
        os.stat(path)
    except:
        os.mkdir(path)
    
    with open("{}/{}.json".format(path,influencer),'wb') as f:
        
        try:
            df= json.load(f)
        except:
            df= {}
        finally:
            df[key]= data
        
        json.dump(df,codecs.getwriter('utf-8')(f), ensure_ascii=False, default = lambda x: None)
