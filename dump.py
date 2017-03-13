import argparse
import logging
import os
import subprocess

# Configure AWS credentials before continue
# http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files

logger = logging.getLogger('dump')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fileHandler = logging.FileHandler('log.log', mode='w')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Path to place the public data files', required=True)
parser.add_argument('-f', '--format', help='Data format', required=False, choices=['xml','json'], default='xml')
parser.add_argument('-v', '--version', help='ORCID message version', required=False, choices=['1.2','2.0'], default='2.0')
args = parser.parse_args()

format = args.format
path = args.path if args.path.endswith('/') else (args.path + '/')
version = '1-2' if args.version == '1.2' else '2-0'
bucket_s3_uri = 's3://orcid-public-data-dump-api-{}-{}-{}'

#---------------------------------------------------------
# Creates a directory if it doesn't exists
#---------------------------------------------------------
def create_directory(path):	
	if not os.path.exists(path):
		os.makedirs(path)

# If the given directory doesn't exists throw an exception		
if not os.path.exists(path):
	sys.exit('Destination ' + path + ' not found')
	
logger.info('About to start syncing local folder with s3 buckets')	
for i in range(0, 11):	
	checksum = str(i) if i != 10 else 'x'	
	directory_path = path + checksum
	bucket_name = bucket_s3_uri.format(version, format, checksum)
	create_directory(directory_path)
	logger.info('About to sync bucket %s on folder %s', bucket_name, directory_path)	
	aws_command = 'aws s3 sync ' + bucket_name + ' ' + directory_path
	logger.info(aws_command)
	subprocess.call(aws_command, shell=True)	
	logger.info('%s is now up to date with bucket %s', directory_path, bucket_name)

logger.info('Sync process is done')	