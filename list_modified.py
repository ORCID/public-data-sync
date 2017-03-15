import boto3
import logging
import iso8601
from datetime import datetime

logger = logging.getLogger('list_modified')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = logging.FileHandler('list_modified.log', mode='w')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

last_modified = iso8601.parse_date('2017-02-15 20:13:11+00:00')
version = '1-2'
format = 'xml'

s3client = boto3.client('s3')

bucket_s3_uri = 'orcid-public-data-dump-api-{}-{}-{}'

def mark_as_modified(name, last_modified):
	with open('modified.txt', 'a') as myfile:
		myfile.write(name + ':' + last_modified + '\n')

for i in range(0, 11):
	checksum = str(i) if i != 10 else 'x'	
	bucket_name = bucket_s3_uri.format(version, format, checksum)	
	paginator = s3client.get_paginator('list_objects')
	page_iterator = paginator.paginate(Bucket=bucket_name)
	for page in page_iterator:
		for element in page['Contents']:
			logger.info(str(element['Key']) + ': ' + str(element['LastModified']))
			element_last_modified = iso8601.parse_date(str(element['LastModified']))
			logger.info(str(element['LastModified']) + ' -> ' + str(element_last_modified))
			if element_last_modified > last_modified:
				mark_as_modified(str(element['Key']), str(element_last_modified))