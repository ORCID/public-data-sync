## ORCID public data dump

The public data dump contains a snapshot of all public data in the ORCID Registry associated with an ORCID record that was created or claimed by an individual.

This script is intended to allow ORCID members to access the data dump on demand, allowing them to be up to date with the latest public data in the ORCID registry.

## Technical description

This script will synchronize a given folder with the latest content available in the (Amazon S3)[https://aws.amazon.com/es/s3] ORCID data dump repository.

When the synchronization process starts, the script will create a set of folders that will contain all ORCID records distributed by the (checksum)[http://support.orcid.org/knowledgebase/articles/116780-structure-of-the-orcid-identifier] of the ORCID ID.

The first time this script runs all records will be copied over your local path, however, any subsequent executing of this script will synchronize the existing data and fetch only the records that have been modified or the ones that has been created since the last time.

## Quick setup

1. Contact the ORCID CES team to get a set of (Amazon AWS)[https://aws.amazon.com] credentials to access the ORCID public record script.

2. Install (python 2.7.6+)[https://www.python.org/download/releases/2.7/]

3. Install the (python PIP)[https://pip.pypa.io/en/stable/installing/] module

4. Install script dependencies:
  * pip2 install -r requirements.txt

5. Configure your (Amazon AWS) credentials[https://aws.amazon.com]:
  * (Configure Amazon AWS credentials)[http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-using-examples]

6. Verify you have at least 250GB available in your hard drive to store the ORCID public data dump
 
## Running the script

To start the sync process, you should provide the following params: 

* Required:
   * p: Local path where you want to place the ORCID data dump
* Optional:
   * f: The public data dump is provided in two different formats XML and JSON, the default one is XML
   * v: The public data dump is provided in the two main API versions, 1.2 and 2.0, the default one is 1.2
   
So, to start the sync process, you should start the script providing at least the path parameter, as follows:   

python dump.py -p `<PATH>`

## Q&A

+ How do I get a set of credentials to get the data dump?

TBD

+ How long does the sync process takes?

That will depend on you hardware configuration and the bandwidth you have, however, the process could be faster by increasing the (number of concurrent elements)[http://docs.aws.amazon.com/cli/latest/topic/s3-config.html] we sync at the same time
