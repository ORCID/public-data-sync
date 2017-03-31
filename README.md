## ORCID public data sync

The public data sync contains a snapshot of all public data in the ORCID Registry associated with any ORCID record that was created or claimed by an individual. The public data modified sync is a snapshot of all public data on records which have been modified in the last hour.

These are Python scripts, based on the Amazon AWS CLI API; it is just a reference implementation intended to show ORCID members how to access the public data sync on demand allowing them to be up to date with the latest public data in the ORCID registry.

Members can create their own implementation using the different APIs that Amazon provides to access S3: 

| API | URL |
| --- | --- |
| CLI | http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html |
| REST API | http://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html |
| Python SDK | https://aws.amazon.com/es/developers/getting-started/python/ |
| Java SDK: | https://aws.amazon.com/es/developers/getting-started/java/ |
| Others: | https://aws.amazon.com/es/developers/getting-started/ |

## Technical description

These scripts will synchronize a given folder with the latest content available in the [Amazon S3](https://aws.amazon.com/s3) ORCID data sync repository. The sync.py script will sync all public content available, the sync_modified.py script will sync only public content from records modified in the last hour.

When the synchronization process starts, the script will create a set of folders that will contain all ORCID records distributed by the [checksum](http://support.orcid.org/knowledgebase/articles/116780-structure-of-the-orcid-identifier) of the ORCID ID.

The first time these script run, all records will be copied over your local path, however, any subsequent executing of the scripts will synchronize the existing data and fetch only the records that have been modified or the ones that has been created since the last time.

## Quick setup

1. Contact the ORCID team at [support@orcid.org](mailto:support@orcid.org) requesting a set of [Amazon AWS](https://aws.amazon.com) credentials to access the ORCID public record script.

2. Install [python 2.7.6+](https://www.python.org/download/releases/2.7/)

3. Install the [python PIP](https://pip.pypa.io/en/stable/installing/) module

4. Install script dependencies:
  * pip2 install -r public-data-sync/requirements.txt

5. Configure your [Amazon AWS credentials](https://aws.amazon.com):

  * AWS Access Key ID: Provided by ORCID
  * AWS Secret Access Key: Provided by ORCID
  * Default region name: Your region, see [Specifying AWS Regions](http://docs.aws.amazon.com/powershell/latest/userguide/pstools-installing-specifying-region.html) for more information
  * Default output format: XML
  * For more information see [Configure Amazon AWS credentials](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-using-examples)

6. If you are runing sync.py, verify you have at least 250GB available in your hard drive to store the ORCID public data sync
 
## Running the script

Script params: 

* Required:
   * p: Local path where you want to place the ORCID data dump
* Optional:
   * f: Format, the records are provided in two different formats, XML and JSON, the default one is XML
   * v: Version, the records are provided in the two supported API versions, 1.2 and 2.0, the default one is 2.0
   
Start the sync process providing at least the path parameter, as follows:   

python sync.py -p `<PATH>`
python sync_modified.py -p `<PATH>`

## Q&A

+ How do I get a set of credentials to use the data sync?

Contact the ORCID team at [support@orcid.org](mailto:support@orcid.org). In the message state you are requesting a set of Amazon AWS credentials to access the ORCID public record script. The ORCID team will confirm your access to the script and provide instructions for accessing the credentials via Passpack (the same method used when issuing ORCID API credentials).

+ Who can use the data sync process?

The data sync process is currently being beta-tested. More information will be provided when the test period is complete.

+ How long does the data sync process takes?

That will depend on you hardware configuration and the bandwidth you have, however, the process could be faster by increasing the [number of concurrent elements](http://docs.aws.amazon.com/cli/latest/topic/s3-config.html) synced at the same time.
