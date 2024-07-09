import argparse
import logging
import os
import os.path
import subprocess
import boto3
from multiprocessing import Pool
from datetime import datetime
from datetime import timedelta
import CustomLogHandler
import shutil
import concurrent.futures

logger = logging.getLogger('sync')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = CustomLogHandler.CustomLogHandler('sync.log')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

summaries_bucket = 'v2.0-summaries'
activities_bucket = 'v2.0-activities'

date_format = '%Y-%m-%d %H:%M:%S.%f'
date_format_no_millis = '%Y-%m-%d %H:%M:%S'

now = datetime.now()
month = str(now.month)
year = str(now.year)

#---------------------------------------------------------
# Validates an integer is positive
#---------------------------------------------------------
def integer_param_validator(value):    
    if int(value) <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid, please specify a positive value greater than 0" % value)
    return int(value)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Path to place the public data files', default='./')
parser.add_argument('-s', '--summaries', help='Download summaries', action='store_true')
parser.add_argument('-a', '--activities', help='Download activities', action='store_true')
parser.add_argument('-t', '--tar', help='Compress the dump', action='store_true')
parser.add_argument('-d', '--days', help='Days to sync', type=integer_param_validator)
parser.add_argument('-l', '--log', help='Set the logging level, DEBUG by default', default='DEBUG')
parser.add_argument('-max', '--max_threads', help='Maximum number of threads', type=integer_param_validator, default=10)
args = parser.parse_args()

path = args.path if args.path.endswith('/') else (args.path + '/')
path = path + 'ORCID_public_data_files/'
download_summaries = args.summaries
download_activities = args.activities
log_level = args.log
days_to_sync = args.days
tar_dump = args.tar
max_threads = args.max_threads
records_to_sync = []

match log_level:
	case 'DEBUG':
		logger.setLevel(logging.DEBUG)
	case 'INFO':
		logger.setLevel(logging.INFO)
	case 'WARN':
		logger.setLevel(logging.WARN)
	case _:
		logger.setLevel(logging.ERROR)

# Create a client
s3client = boto3.client('s3')

def sync_summaries(orcid_to_sync):
	suffix = orcid_to_sync[-3:]
	prefix = suffix + '/' + orcid_to_sync + '.xml'
	file_path = path + 'summaries/' + suffix + '/'
	file_name = orcid_to_sync + '.xml'
	try:
		if not os.path.exists(file_path):
			os.makedirs(file_path)
	except:
		pass
	logger.debug('Downloading ' + file_name + ' to ' + file_path)

	try:
		# Downloading the file
		s3client.download_file(summaries_bucket, prefix, file_path + file_name)
	except ClientError as e:
		logger.exception('Error fetching ' + element)
		logger.exception(e)

def sync_activities(element):
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
	logger.debug('Downloading ' + name + ' to ' + file_path)
	try:
		if not os.path.exists(file_path):
			os.makedirs(file_path)
	except:
		pass
	try:
		# Downloading the file
		s3client.download_file(activities_bucket, element, file_path + name);	
	except ClientError as e:
		logger.exception('Error fetching ' + element)
		logger.exception(e)
	# aws cli will remove the files but not the folders so, 
	# we need to check if the folders are empty and delete it
	if os.path.exists(local_directory) and os.path.isdir(local_directory): 
		for root, dirs, files in os.walk(local_directory):
			for dir in dirs:
				if not os.listdir(local_directory + '/' + dir):				
					logger.info('Deleting %s because it is empty', local_directory + '/' + dir)
					shutil.rmtree(local_directory + '/' + dir)
				if not os.listdir(local_directory):
					logger.info('Deleting %s because because it is empty', local_directory)
					shutil.rmtree(local_directory)
				# delete the suffix folder if needed
				if not os.listdir(path + 'activities/' + suffix):
					logger.info('Deleting %s because because it is empty', path + 'activities/' + suffix)
					shutil.rmtree(path + 'activities/' + suffix)
                    
def process_activities(orcid_to_sync):
    suffix = orcid_to_sync[-3:]
    prefix = suffix + '/' + orcid_to_sync
    paginator = s3client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=activities_bucket, Prefix=prefix, PaginationConfig={'PageSize': 1000})

    page_count = 1
    for page in page_iterator:		
        logger.info('Activities page count: ' + str(page_count))		
        page_count += 1
        elements = []
        if 'Contents' in page:
            for element in page['Contents']:
                elements.append(element['Key'])
        else:
            logger.warn('Unable to find activities for %s', orcid_to_sync)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(sync_activities, elements)

        continuation_token = None
        try:
            continuation_token = page['NextContinuationToken']
        except:
            logger.debug('No more continuation tokens')
        file = open('activities_next_continuation_token.config','w') 
        file.write(str(continuation_token))  
        file.close()

#---------------------------------------------------------
# Main process
#---------------------------------------------------------
if __name__ == "__main__":
	start_time = datetime.now()

	# Download the lambda file
	logger.info('Downloading the lambda file')	
	s3client.download_file('orcid-lambda-file', 'last_modified.csv.tar', 'last_modified.csv.tar');	
	# Decompress the file
	logger.info('Decompressing the lambda file')	
	subprocess.call('tar -xzvf last_modified.csv.tar', shell=True)

	# Look for the config file
	last_sync = None
	if days_to_sync is not None: 
		last_sync = (datetime.now() - timedelta(days=days_to_sync))
	elif os.path.isfile('last_ran.config'):
		f = open('last_ran.config', 'r')
		date_string = f.readline()		
		last_sync = datetime.strptime(date_string, date_format)	
	else:
		last_sync = (datetime.now() - timedelta(days=30))
		
	logger.info('Sync records modified after %s', str(last_sync))		

	is_first_line = True
	
	for line in open('last_modified.csv', 'r'):
		if is_first_line:
			is_first_line = False
			continue
		line = line.rstrip('\n')
		elements = line.split(',')	
		orcid = elements[0]
		
		last_modified_str = elements[3]
		try:
			last_modified_date = datetime.strptime(last_modified_str, date_format)
		except ValueError:
			last_modified_date = datetime.strptime(last_modified_str, date_format_no_millis)
						
		if last_modified_date >= last_sync:
			records_to_sync.append(orcid) 
			if len(records_to_sync) % 10000 == 0:
				logger.info('Records to sync so far: %s', len(records_to_sync))
		else:
			# Since the lambda file is ordered by last_modified date descendant, 
			# when last_modified_date < last_sync we don't need to parse any more lines
			break
	
	logger.info('Records to sync: %s', len(records_to_sync))
	
	pool = Pool(processes=max_threads)

	if download_summaries:
		logger.info('Syncing summaries')
		pool.map(sync_summaries, records_to_sync)

	if download_activities:
		logger.info('Syncing activities')
		pool.map(process_activities, records_to_sync)

	pool.close()
	pool.join()

	logger.info('All files are in sync now')

	# keep track of the last time this process ran
	file = open('last_ran.config','w') 
	file.write(str(start_time))  
	file.close()
	logger.info('last_ran.config is ready')
	logger.info('End of script')
