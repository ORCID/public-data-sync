import argparse
import logging
import os
import os.path
import subprocess
from multiprocessing import Process
from datetime import datetime
from datetime import timedelta
import CustomLogHandler
import shutil

logger = logging.getLogger('sync')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = CustomLogHandler.CustomLogHandler('sync.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

summaries_bucket = 's3://v2.0-summaries/'
activities_bucket = 's3://v2.0-activities/'

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
args = parser.parse_args()

path = args.path if args.path.endswith('/') else (args.path + '/')
path = path + 'ORCID_public_data_files/'
download_summaries = args.summaries
download_activities = args.activities
days_to_sync = args.days
tar_dump = args.tar

#---------------------------------------------------------
# Main process
#---------------------------------------------------------
if __name__ == "__main__":
	start_time = datetime.now()

	# Download the lambda file
	logger.info('Downloading the lambda file')	
	subprocess.call('aws s3 cp s3://orcid-lambda-file/last_modified.csv.tar last_modified.csv.tar', shell=True)
	
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
		
	records_to_sync = []

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
			logger.info('Adding %s to the sync list, since it was modified on %s', orcid, last_modified_str)
			records_to_sync.append(orcid) 
		else:
			# Since the lambda file is ordered by last_modified date descendant, 
			# when last_modified_date < last_sync we don't need to parse any more lines
			break
	
	logger.info('Records to sync: %s', len(records_to_sync))
	
	for orcid_to_sync in records_to_sync:
		suffix = orcid_to_sync[-3:]
		if download_summaries:
			prefix = suffix + '/' + orcid_to_sync + '.xml'
			subprocess.call('aws s3 cp ' + summaries_bucket + prefix + ' ' + path + 'summaries/' + prefix, shell=True)
		if download_activities:
			prefix = suffix + '/' + orcid_to_sync + '/'
			local_directory = path + 'activities/' + prefix			
			# fetch data from S3
			logger.info('aws s3 sync ' + activities_bucket + prefix + ' ' + local_directory + ' --delete')
			subprocess.call('aws s3 sync ' + activities_bucket + prefix + ' ' + local_directory + ' --delete', shell=True)
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

	# keep track of the last time this process ran
	file = open('last_ran.config','w') 
	file.write(str(start_time))  
	file.close()
			
						