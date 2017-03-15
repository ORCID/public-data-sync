## ORCID public data sync

The public data sync contains a snapshot of all public data in the ORCID Registry associated with any ORCID record that was created or claimed by an individual.

This is a Python script, based on the Amazon AWS CLI API; it is just a reference implementation intended to show ORCID members how to access the data dump on demand allowing them to be up to date with the latest public data in the ORCID registry.

Members can create their own implementation using the different APIs that Amazon provides to access S3: 

| API | URL |
| --- | --- |
| CLI | http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html |
| REST API | http://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html |
| Python SDK | https://aws.amazon.com/es/developers/getting-started/python/ |
| Java SDK: | https://aws.amazon.com/es/developers/getting-started/java/ |
| Others: | https://aws.amazon.com/es/developers/getting-started/ |

## Technical description

This script will synchronize a given folder with the latest content available in the [Amazon S3](https://aws.amazon.com/es/s3) ORCID data dump repository.

When the synchronization process starts, the script will create a set of folders that will contain all ORCID records distributed by the [checksum](http://support.orcid.org/knowledgebase/articles/116780-structure-of-the-orcid-identifier) of the ORCID ID.

The first time this script runs all records will be copied over your local path, however, any subsequent executing of this script will synchronize the existing data and fetch only the records that have been modified or the ones that has been created since the last time.

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

6. Verify you have at least 250GB available in your hard drive to store the ORCID public data dump
 
## Running the script

Script params: 

* Required:
   * p: Local path where you want to place the ORCID data dump
* Optional:
   * f: Format, the public data dump is provided in two different formats XML and JSON, the default one is XML
   * v: Version, the public data dump is provided in the two supported API versions, 1.2 and 2.0, the default one is 2.0
   
Start the sync process providing at least the path parameter, as follows:   

python dump.py -p `<PATH>`

## Q&A

+ How do I get a set of credentials to use the data sync?

Contact the ORCID team at [support@orcid.org](mailto:support@orcid.org). In the message state you are requesting a set of Amazon AWS credentials to access the ORCID public record script. The ORCID team will confirm your access to the script and provide instructions for accessing the credentials via Passpack (the same method used when issuing ORCID API credentials).

+ Who can use the data sync process?

The data sync process is currently being beta-tested. More information will be provided when the test period is complete.

+ How long does the data sync process takes?

That will depend on you hardware configuration and the bandwidth you have, however, the process could be faster by increasing the [number of concurrent elements](http://docs.aws.amazon.com/cli/latest/topic/s3-config.html) synced at the same time.
