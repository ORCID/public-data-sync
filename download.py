import argparse
import logging
import os
import subprocess
from multiprocessing import Process
from datetime import datetime
import CustomLogHandler

# Configure AWS credentials before continue
# http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files

logger = logging.getLogger('download')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = CustomLogHandler.CustomLogHandler('download.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

summaries_bucket = 's3://v2.0-summaries'
activities_bucket = 's3://v2.0-activities'

now = datetime.now()
month = str(now.month)
year = str(now.year)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Path to place the public data files', default='./')
parser.add_argument('-s', '--summaries', help='Download summaries', action='store_true')
parser.add_argument('-a', '--activities', help='Download activities', action='store_true')
parser.add_argument('-t', '--tar', help='Compress the dump', action='store_true')
args = parser.parse_args()

path = args.path if args.path.endswith('/') else (args.path + '/')
path = path + 'ORCID_public_data_files/'
download_summaries = args.summaries
download_activities = args.activities
tar_dump = args.tar

#---------------------------------------------------------
# Executes the given download command
#---------------------------------------------------------
def download(download_command):
	logger.info('Running command ' + download_command)
	subprocess.call(download_command, shell=True)
	
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
	if download_summaries:
		summaries_aws_command = 'aws s3 sync ' + summaries_bucket + ' ' + path + 'summaries'
		download(summaries_aws_command)
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
	if download_activities:
		activites_aws_command = 'aws s3 sync ' + activities_bucket + ' ' + path + 'activities'	
		download(activites_aws_command)
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
