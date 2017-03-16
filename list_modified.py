import boto3
import datetime
import iso8601
import logging

logger = logging.getLogger('list_modified')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = logging.FileHandler('list_modified.log', mode='w')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

modified_since = iso8601.parse_date(str(datetime.datetime.utcnow() - datetime.timedelta(minutes=60)));
logger.info('Fetching elements modified since:' + str(modified_since))
version = '1-2'
format = 'xml'

s3client = boto3.client('s3')

bucket_s3_uri = 'orcid-public-data-dump-api-{}-{}-{}'

def mark_as_modified(name, modified_since):
	with open('modified.txt', 'a') as myfile:
		myfile.write(name + ':' + modified_since + '\n')

for i in range(0, 11):
	checksum = str(i) if i != 10 else 'x'	
	bucket_name = bucket_s3_uri.format(version, format, checksum)	
	paginator = s3client.get_paginator('list_objects')
	logger.info('Processing: ' + bucket_name)
	page_iterator = paginator.paginate(Bucket=bucket_name)
	for page in page_iterator:
		for element in page['Contents']:
			element_last_modified = iso8601.parse_date(str(element['LastModified']))
			if element_last_modified >= modified_since:
				mark_as_modified(str(element['Key']), str(element_last_modified))