import argparse
import logging
import os
import subprocess
import boto3
from multiprocessing import Pool
from multiprocessing import Process
from datetime import datetime
from botocore.exceptions import ClientError
import CustomLogHandler

# Configure AWS credentials before continue
# http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files

logger = logging.getLogger('download')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = CustomLogHandler.CustomLogHandler('download.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

summaries_bucket = 'v2.0-summaries'
activities_bucket = 'v2.0-activities'

now = datetime.now()
month = str(now.month)
year = str(now.year)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Path to place the public data files', default='./')
parser.add_argument('-s', '--summaries', help='Download summaries', action='store_true')
parser.add_argument('-a', '--activities', help='Download activities', action='store_true')
parser.add_argument('-t', '--tar', help='Compress the dump', action='store_true')
parser.add_argument('-r', '--recovery', help='Start recovery process', action='store_true')
parser.add_argument('-max', '--max_threads', default=60)
parser.add_argument('-v', '--verbose', help='Print the name of the downloading files.', action='store_true')
args = parser.parse_args()

path = args.path if args.path.endswith('/') else (args.path + '/')
path = path + 'ORCID_public_data_files/'
download_summaries = args.summaries
download_activities = args.activities
recovery = args.recovery
tar_dump = args.tar
verbose  = args.verbose
MAX_THREADS = int(args.max_threads)

# Create a client
s3client = boto3.client('s3')

#---------------------------------------------------------
# Download a single summary file
#---------------------------------------------------------
def download_summary(element):
	global s3client
	global summaries_bucket
	
	components = element.split('/')	
	# Checksum
	checksum = components[0]
	# File name 
	name = components[1]
	
	if verbose:
		print (name)

	file_path = path + 'summaries/' + checksum + '/'
	logger.info('Downloading ' + name + ' to ' + file_path)
	
	# Create the path directory
	try:
		if not os.path.exists(file_path):
			os.makedirs(file_path)
	except OSError, e:			
		pass
		
	try:
		# Downloading the file
		s3client.download_file(summaries_bucket, element, file_path + name);	
	except ClientError as e:
		logger.exception('Error fetching ' + element)
		logger.exception(e)

#---------------------------------------------------------
# Download a single activity file
#---------------------------------------------------------
def download_activity(element):
	global s3client		
	global activities_bucket
	
	components = element.split('/')	
	# Checksum
	checksum = components[0]
	# ORCID
	orcid = components[1]
	# Activity type
	type = components [2]
	# File name 
	name = components[3]
	
	file_path = path + 'activities/' + checksum + '/' + orcid + '/' + type + '/'
	logger.info('Downloading ' + name + ' to ' + file_path)
	
	# Create the path directory
	try:
		if not os.path.exists(file_path):
			os.makedirs(file_path)
	except OSError, e:			
		pass
		
	try:
		# Downloading the file
		s3client.download_file(activities_bucket, element, file_path + name);	
	except ClientError as e:
		logger.exception('Error fetching ' + element)
		logger.exception(e)
		
#---------------------------------------------------------
# Compress the given directory
#---------------------------------------------------------	
def compress(tar_path, directory_name):		
	global path
	# Compress directory
	logger.info('Compressing ' + tar_path + ' -C ' + path + ' directory_name: ' + directory_name)	
	proc = subprocess.Popen(['tar', '-czf', tar_path, '-C', path, directory_name])
	proc.communicate()	
	logger.info(tar_path + ' compressed')	
	
#---------------------------------------------------------
# Process summaries
#---------------------------------------------------------	
def process_summaries():
	global path
	global summaries_bucket
	global month
	global year
	global recovery
	if download_summaries:
		# Create the paginator
		paginator = s3client.get_paginator('list_objects_v2')
		
		# Create a PageIterator from the Paginator
		page_iterator = None
		if recovery:
			f = open('summary_next_continuation_token.config', 'r')
			continuation = f.readline()
			page_iterator = paginator.paginate(Bucket=summaries_bucket, ContinuationToken=continuation, PaginationConfig={'PageSize': 1000})
		else:
			page_iterator = paginator.paginate(Bucket=summaries_bucket, PaginationConfig={'PageSize': 1000})		
		
		page_count = 1
		for page in page_iterator:
			logger.info('Summaries page count: ' + str(page_count))
			page_count += 1
			elements = []
			for element in page['Contents']:
				elements.append(element['Key'].decode('utf-8'))
			pool = Pool(processes=MAX_THREADS)		
			pool.map(download_summary, elements)
			pool.close()
			pool.join()
			continuation_token = None
			try:
				continuation_token = page['NextContinuationToken']
			except:
				logger.info('No more continuation tokens')			
			file = open('summary_next_continuation_token.config','w') 
			file.write(str(continuation_token))  
			file.close()
		if tar_dump:
			summaries_dump_name_xml = 'ORCID-API-2.0_xml_' + month + '_' + year + '.tar.gz'
			compress(summaries_dump_name_xml, 'summaries')

#---------------------------------------------------------
# Process activities
#---------------------------------------------------------
def process_activities():
	global path
	global activities_bucket
	global month
	global year
	global recovery
	if download_activities:
		# Create the paginator
		paginator = s3client.get_paginator('list_objects_v2')
		# Create a PageIterator from the Paginator
		page_iterator = None
		if recovery:
			f = open('activities_next_continuation_token.config', 'r')
			continuation = f.readline()
			page_iterator = paginator.paginate(Bucket=activities_bucket, ContinuationToken=continuation, PaginationConfig={'PageSize': 1000})		
		else:
			page_iterator = paginator.paginate(Bucket=activities_bucket, PaginationConfig={'PageSize': 1000})
		
		page_count = 1
		for page in page_iterator:
			logger.info('Activities page count: ' + str(page_count))
			page_count += 1
			elements = []
			for element in page['Contents']:
				elements.append(element['Key'].decode('utf-8'))
			pool = Pool(processes=MAX_THREADS)		
			pool.map(download_activity, elements)
			pool.close()
			pool.join()	
			continuation_token = None
			try:
				continuation_token = page['NextContinuationToken']
			except:
				logger.info('No more continuation tokens')
			file = open('activities_next_continuation_token.config','w') 
			file.write(str(continuation_token))  
			file.close()			
		if tar_dump:
			activities_dump_name_xml = 'ORCID-API-2.0_activities_xml_' + month + '_' + year + '.tar.gz'
			compress(activities_dump_name_xml, 'activities')
		
#---------------------------------------------------------
# Main process
#---------------------------------------------------------
if __name__ == "__main__":
	if download_summaries is False and download_activities is False:
		logger.error('Please specify the elements you want to download using the -s or -a flag')
		raise

	# Create the path directory
	if not os.path.exists(path):
		os.makedirs(path)
	
	start_time = datetime.now()
	
	logger.info('About to start syncing local folder with s3 buckets')	

	# Define threads
	summaries_thread = Process(target=process_summaries)
	activities_thread = Process(target=process_activities)

	# Start threads
	summaries_thread.start()
	activities_thread.start()
	
	# Join threads
	summaries_thread.join()
	activities_thread.join()
	
	logger.info('Download process is done')	
	
	# keep track of the last time this process ran
	file = open('last_ran.config','w') 
	file.write(str(start_time))  
	file.close()