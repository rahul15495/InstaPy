import os
import shutil
import ntpath 
import sys
import time
import driver
import glob
import configparser
from itertools import chain
import postMLData
import json
from logger import *
from stats import append_stats
import datetime

send_alert= True

if send_alert:
	import sendMail


export_path= os.environ['HOME']+'/iPROCESS/S3/processed/'
save_path= os.environ['HOME']+'/iPROCESS/S3/output/'
error_path=os.environ['HOME']+'/iPROCESS/S3/errored/'
valid_image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"] #specify your valid extensions here
valid_license_types= ['SSD', 'ID', 'ED']

get_filename= lambda fname:".".join(fname.split('.')[:-1])

debug= True


def credit_decrement(produce,license_type):
	# decrement the credit using ini parser aka configparser

	
	# instantiate
	config = configparser.ConfigParser()

	# parse existing file
	config.read('credit_meta.ini')

	# read values from a produce section
	SSD_credit = config.getint(str(produce), 'SSD')
	ID_credit = config.getint(str(produce), 'ID')
	ED_credit = config.getint(str(produce), 'ED')

	value_reductant = 0
	if license_type.upper() == 'SSD':
		value_reductant = SSD_credit

	elif license_type.upper() =='ED':
		value_reductant = ED_credit

	elif license_type.upper() =='ID':
		value_reductant = ID_credit
	else:
		value_reductant=0
		logging.debug("invalid license type {}".format(license_type))

	return(value_reductant)


def batch_processor(path,lic_type,produce,uniqueID,callbackURL,sizeBucket,RangeType,Customer_id,variety):

	files= []
	for ext in valid_image_extensions:
		_files= glob.glob(path+'*'+ext)
		if len(_files)>0:
			files+=_files

	number_of_files= len(files)


	total_success=0

	for f in files:
		logging.debug(f)
		success = mono_processor(f,lic_type,produce,uniqueID,callbackURL,sizeBucket,RangeType,Customer_id,variety)
		total_success+= success
	
	return(total_success,number_of_files)  



def mono_processor(path,lic_type,produce,uniqueID,callbackURL,sizeBucket,RangeType,Customer_id,variety):
	# start processing
	start_time= time.clock()
	status = "ERROR"
	fname= path.split('/')[-1]
	success,json_data = driver.run(path,save_path,lic_type,produce,uniqueID,sizeBucket,RangeType,callbackURL,Customer_id,variety)
	logging.debug("MONO_PROCESS_STATUS"+ ': {}'.format(success))
	if success==1:
		export_image(path,export_path+fname)
		status = "SUCCESS"
	else:
		export_image(path, error_path+fname)
		if send_alert:
			sendMail.sendMail("Error Encountered on {}".format(str(datetime.date.today())),"filename: {}\nmessage: {}".format(fname, json_data))
		else:
			pass
	try:
		logging.debug(json_data)
		_fname = get_filename(fname)
		pTime= (time.clock() - start_time)
		postMLData.postMLData(callbackURL,json_data,status,uniqueID,_fname, pTime)
		
	except:
		logging.debug("error posting ::"+json_data+ "to "+callbackURL)
		if send_alert:
			sendMail.sendMail("Error Encountered on {}".format(str(datetime.date.today())),"filename: {}\nmessage: {}".format(fname, "error posting ::"+json_data+ " to "+callbackURL))
		else:
			pass
		logging.debug(traceback.format_exc())
        # send email
		#sendMail.sendMail("Error Encountered","Error while prcessing Image {}".format(fname))
		
	
	return(success)  


def process_image(params):

	validation_check_error=0
	error_msg= " "

	start_time = time.clock()
	# catching params
	path = params[1]
	process_flag = int(params[2]) # type of processing required
	lic_type = str(params[3])  #type of lic- SSD, ID or ED
	produce = str(params[4])	#type of produce 
	variety = str(params[5])
	uniqueID = str(params[6])
	sizeBucket = params[7]
	callbackURL = str(params[8])
	RangeType= str(params[9])
	Customer_id= str(params[10])
	# argument check
	if len(params) !=11 :
		logging.debug("error: The number of argument recieved is not matched\n"
			"Need 5 aguments as follow:\n"
			"<path> <processing type> <license> <produce> <variety> <uniqueID> <sizeBucket> <callbackURL>")
		validation_check_error= 1



	# extension check

	if lic_type.upper() not in valid_license_types:
		msg= " invalid license type"

		logging.debug("error: {} {}".format(msg,lic_type))
		error_msg= error_msg+ msg
		validation_check_error= 1


	if process_flag == 0:
		extension = os.path.splitext(path)[1]
		if extension.lower() not in valid_image_extensions:
			msg= " Format not supported!"

			logging.debug("error: {}".format(msg))
			error_msg= error_msg+ msg
			validation_check_error= 1

	if process_flag == 1:
		_valid_image_extensions = [item.lower() for item in valid_image_extensions]
		for file in (os.listdir(path)):
			extension = os.path.splitext(file)[1]
			if extension.lower() not in _valid_image_extensions:

				msg= " Format not supported!"

				logging.debug("error: {}".format(msg))
				error_msg= error_msg+ msg
				validation_check_error= 1



	# let's set the processing status = 0. After processing it has to set to 1.

	status = 0
	if validation_check_error==0:

		if process_flag == 0:
			success = mono_processor(path,lic_type,produce,uniqueID,callbackURL,sizeBucket,RangeType,Customer_id,variety)
			status= success
		else:
			total_success, number_of_files = batch_processor(path,lic_type,produce,uniqueID,callbackURL,sizeBucket,RangeType,Customer_id,variety)
			if (number_of_files- total_success)==0:
				status= success
			else:
				logging.debug('{}'.format(total_success) +' of {}'.format(number_of_files)+' processed')
	else:
		status=0

		fname= path.split('/')[-1]
		_fname= get_filename(fname)

		pTime= (time.clock() - start_time)

		logging.debug(error_msg)

		error_msg= json.dumps({"error" :error_msg})

		postMLData.postMLData(callbackURL,error_msg,status,uniqueID,_fname, pTime)

		export_image(path, error_path+fname)

		if send_alert:
			sendMail.sendMail("Error Encountered on {}".format(str(datetime.date.today())),"filename: {}\nmessage: {}".format(fname,error_msg))


	# credit decrements only after sucessful processing of images
	DCRM_counter =0
	if status!=0:
		DCRM_counter=credit_decrement(produce,lic_type)
		logging.debug("DCRM_count: {}".format(DCRM_counter))
		logging.debug("Processing sucessful")
		append_stats(callbackURL,'processed')
	
	elif status==0:
		logging.debug("error: Status flag not set after processing")
		append_stats(callbackURL,'errored')

	execute_time= (time.clock() - start_time)

	if debug:
		logging.debug("{}".format(execute_time)+" seconds")
		logging.debug("**************************************************************")
		

	return(status,DCRM_counter,execute_time)

def export_image(src, dst):
	shutil.move(src,dst)


if __name__ =="__main__":

	process_image()
