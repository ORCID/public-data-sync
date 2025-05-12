import argparse
import os
import xml.etree.ElementTree as ET
import pymongo
from pymongo.errors import BulkWriteError
import logging
from datetime import datetime

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Path to place the public data files', default='./')
parser.add_argument('-host', '--host', help='MongoDB host', default='localhost')
parser.add_argument('-port', '--port', help='MongoDB port', default=27017)
parser.add_argument('-u', '--username', help='MongoDB username', default='')
parser.add_argument('-psword', '--password', help='MongoDB password', default='')
parser.add_argument('-db', '--database', help='MongoDB database name', default='')
parser.add_argument('-c', '--collection', help='MongoDB collection name', default='')
args = parser.parse_args()

path = args.path if args.path.endswith('/') else (args.path + '/')
ip = args.host
port = int(args.port)
user_name = args.username
psword = args.password
db_name = args.database
collection_name = args.collection
client = pymongo.MongoClient(ip, int(port), username=user_name, password=psword, maxPoolSize=10000)
db = client[db_name]
collection = db[collection_name]

def bulk_upsert_orcid_files(file_paths):
    bulk_operations = []
    processed_count = 0

    for file_path in file_paths:
        try:
            orcid_id = os.path.basename(file_path)[:-4]
            with open(file_path, 'r', encoding='utf-8') as file:
                xml_content = file.read()

            if len(xml_content.encode('utf-8')) >= 16 * 1024 * 1024:
                logger.warning(f"Skipping ORCID {orcid_id} — file too large")
                continue
            last_updated = datetime.now()

            document = {
                "_id": orcid_id,
                "xml-content": xml_content,
                "last-updated": last_updated
            }

            bulk_operations.append(
                pymongo.operations.ReplaceOne(
                    {"_id": orcid_id},
                    document,
                    upsert=True
                )
            )
            if len(bulk_operations) == 500:
                try:
                    result = collection.bulk_write(bulk_operations)
                    bulk_operations = []
                except BulkWriteError as bwe:
                    logger.error(f"Bulk write error: {bwe.details}")
                    raise

            processed_count += 1
            if processed_count % 10000 == 0:
                logger.info(f"Processed {processed_count} files")
                print(f"Processed {processed_count} files")

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    if len(bulk_operations) > 0:
        try:
            logger.info(f"Executing bulk upsert for {len(bulk_operations)} documents")
            print(bulk_operations)
            result = collection.bulk_write(bulk_operations)
            logger.info(f"Bulk upsert completed: {result.bulk_api_result}")
            bulk_operations = []
        except BulkWriteError as bwe:
            logger.error(f"Bulk write error: {bwe.details}")
            raise

def list_all_files(directory):
    """
    List all files in the given directory and its subdirectories.

    Args:
        directory (str): The path to the directory to search

    Returns:
        list: A list of file paths
    """
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Create full path for each file
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    return all_files

if __name__ == "__main__":
    #directory_path = '/mnt/data/orcidsync/ORCID_public_data_files/summaries/ORCID_2024_10_summaries/'
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory")
    else:
        files = list_all_files(path)
        print(f"\nFound {len(files)} files in '{path}' and its subdirectories:\n")
        bulk_upsert_orcid_files(files)
