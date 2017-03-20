import argparse
import boto3
import datetime
import iso8601
import logging
import os
import sys
from Queue import Queue
from threading import Thread

logger = logging.getLogger('list_modified')
formatter = logging.Formatter('%(asctime)s %(message)s')
fileHandler = logging.FileHandler('list_modified.log', mode='w')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Path to place downloaded files', required=True)
parser.add_argument('-f', '--format', help='Data format', required=False, choices=['xml','json'], default='xml')
parser.add_argument('-v', '--version', help='ORCID message version', required=False, choices=['1.2','2.0'], default='2.0')
args = parser.parse_args()

modified_since = iso8601.parse_date(str(datetime.datetime.utcnow() - datetime.timedelta(minutes = 60)));
format = args.format
version = '1-2' if args.version == '1.2' else '2-0'
local_path = args.path if args.path.endswith('/') else (args.path + '/')

if not os.path.exists(local_path):
	sys.exit('Destination ' + local_path + ' not found')

s3client = boto3.client('s3')
bucket_s3_uri = 'orcid-public-data-dump-api-{}-{}-{}'

class SyncWorker(Thread):
   def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue

   def run(self):
       while True:
           # Get the work from the queue and expand the tuple
           index = self.queue.get()
           traverse_bucket(index)
           self.queue.task_done()

#---------------------------------------------------------
# Creates a directory if it doesn't exists
#---------------------------------------------------------
def create_directory(path):	
	if not os.path.exists(path):
		os.makedirs(path)

#---------------------------------------------------------
# Download a file from S3
#---------------------------------------------------------
def download(s3_client, prefix, bucket_name, element_name):
	global local_path	
	element_path = local_path + prefix + '/' + element_name
	logger.info('Downloading {} to: {}'.format(element_name, element_path))
	s3_client.download_file(bucket_name, element_name, element_path)	

#---------------------------------------------------------
# Traverse bucket looking for modified elements
#---------------------------------------------------------	
def traverse_bucket(index):
	global local_path
	global modified_since	
	checksum = str(index) if index != 10 else 'x'
	directory_path = local_path + checksum
	create_directory(directory_path)	
	bucket_name = bucket_s3_uri.format(version, format, checksum)	
	logger.info('Iterating bucket {}'.format(bucket_name))
	paginator = s3client.get_paginator('list_objects')
	page_iterator = paginator.paginate(Bucket=bucket_name)
	for page in page_iterator:
		for element in page['Contents']:
			element_last_modified = iso8601.parse_date(str(element['LastModified']))
			if element_last_modified >= modified_since:
				download(s3client, checksum, bucket_name, element['Key'])
	logger.info('Just finished iterating bucket {}'.format(bucket_name))
																						
queue = Queue()
start = datetime.datetime.now()
for index in range(11):
	worker = SyncWorker(queue)
	worker.daemon = True
	logger.info('Starting thread {}'.format(index))
	worker.start()

for index in range(0, 11):
	logger.info('Queueing {}'.format(index))
	queue.put(index)
	
# Causes the main thread to wait for the queue to finish processing all the tasks
queue.join()
logger.info('Just finished the dump, this time it took {}'.format(str(datetime.datetime.now() - start)))








