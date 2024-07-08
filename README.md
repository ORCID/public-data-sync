## ORCID public data sync

The public data sync contains a snapshot of all public data in the ORCID Registry associated with any ORCID record that was created or claimed by an individual. 

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

These scripts will synchronize a given folder with the latest content available in the [Amazon S3](https://aws.amazon.com/s3) ORCID data sync repository. The download.py script will fetch all public content available, the sync.py script will sync the content modified since the last time the download.py or the sync.py script ran, since a given number of days back, or since the last 30 days if none of the options is provided.

When the synchronization process starts, the script will create a set of folders that will contain all ORCID records distributed by the [checksum](http://support.orcid.org/knowledgebase/articles/116780-structure-of-the-orcid-identifier) of the ORCID ID.

Please note that these scripts have been updated to work with Python 3.

## Quick setup

1. Ensure that you are set up to handle the sync files. Verify you have at least 250GB available in your hard drive and are able to process the files (each ORCID records is stored as multiple files). You may want to first look at the [ORCID Public Data File](https://orcid.org/content/download-file) to see an example of what to expect when using the sync process.

2. Contact the ORCID team at [support@orcid.org](mailto:support@orcid.org) requesting a set of [Amazon AWS](https://aws.amazon.com) credentials to access the ORCID public record script.

3. Install [python 3.7.6+](https://www.python.org/downloads/release/python-376/)

4. Install the [python PIP](https://pip.pypa.io/en/stable/installation/) module

5. Install script dependencies:
  * pip3 install -r public-data-sync/requirements.txt

6. Configure your [Amazon AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html):

  * AWS Access Key ID: Provided by ORCID
  * AWS Secret Access Key: Provided by ORCID
  * Default region name: Your region, see [Specifying AWS Regions](http://docs.aws.amazon.com/powershell/latest/userguide/pstools-installing-specifying-region.html) for more information
  * Default output format: XML
  * For more information see [Configure Amazon AWS credentials](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-using-examples)
 
## Running the script download.py script

Objective: This script will fetch all public content available at the time it ran

Script params: 

* Required:
   * p: Local path where you want to place the ORCID data dump
* Optional:
   * s: Use it to sync summaries
   * a: Use it to sync activities
   * t: Use it to create a compressed directory (.tar.gz) for each of the types (activities or summaries) you are syncing 

Start the sync process providing at least the path parameter and -s or -a
   
Examples:    

python download.py -p `<PATH>` -s

This will sync all summaries and put them under the `<PATH>` directory inside a folder called `summaries`

python download.py -p `<PATH>` -s -a

This will sync all activities and summaries and put them under the `<PATH>` directory, the summaries will be inside a folder called `summaries` and the activities will be inside a folder called `activites`

After this process finishes, there will be a config file called `last_ran.config`, which will contain the time this process started.

## Running the script sync.py script

Objective: This script will fetch the public content available at the time it ran and that was modified after a given time

Script params: 

* Required:
   * p: Local path where you want to place the ORCID data dump
* Optional:
   * s: Use it to sync summaries
   * a: Use it to sync activities
   * t: Use it to create a compressed directory (.tar.gz) for each of the types (activities or summaries) you are syncing 
   * d: Use it to indicate the number of days in the past the record will sync, it is not required and if missing, the system will use the `last_ran.config` file to determine which files it have to sync

Start the sync process providing at least the path parameter and -s or -a
   
Examples:    

python sync.py -p `<PATH>` -s

This will sync summaries and put them under the `<PATH>` directory inside a folder called `summaries`

python sync.py -p `<PATH>` -s -a

This will sync activities and summaries and put them under the `<PATH>` directory, the summaries will be inside a folder called `summaries` and the activities will be inside a folder called `activites`

After this process finishes, there will be a config file called `last_ran.config`, which will contain the time this process started.

## Q&A

+ How do I get a set of credentials to use the data sync?

Contact the ORCID team at [support@orcid.org](mailto:support@orcid.org). In the message state you are requesting a set of Amazon AWS credentials to access the ORCID public data sync script. The ORCID team will confirm your access to the script and provide instructions for accessing the credentials via Passpack (the same method used when issuing ORCID API credentials) or encrypted email.

+ Who can use the data sync process?

The data sync process is available to ORCID Premium members. If you are unsure of your organization's membership status contact [support@orcid.org](mailto:support@orcid.org). Everyone is welcome to use the free [ORCID Public Data File](https://orcid.org/content/download-file).

+ How long does the data sync process takes?

That will depend on you hardware configuration and the bandwidth you have, however, the process could be faster by increasing the [number of concurrent elements](http://docs.aws.amazon.com/cli/latest/topic/s3-config.html) synced at the same time.

+ Can I get sync files in other formats?

We only offer the sycn files in ORCID XML using the [2.0 schema](https://github.com/ORCID/ORCID-Source/tree/master/orcid-model/src/main/resources/record_2.0). If you are working with JSON, you may want to consider using the [ORCID Converstion Utility](https://github.com/ORCID/orcid-conversion-lib)

+ Are there other options for tracking changes to ORCID records?

   * Premium members can [set up webhooks](https://github.com/ORCID/ORCID-Source/blob/master/orcid-api-web/tutorial/webhooks.md) to get notifications when specific records they are watching are updated.
   * A Lambda file is available listing the last time each ORCID record was modified, modified records can then be called using the API to see what changes were made.
   * Depending on your use case, you may be able to query the [ORCID API](https://github.com/ORCID/ORCID-Source/tree/master/orcid-api-web). Contact support@orcid.org for help with using the API with your use case.

+ Is this still available in python 2?

For legacy integrations, we provide `requirements.python_2_7.txt` and `download.python_2_7.py` that should run in python 2.7, however, they are not supported anymore and might stop working at any point.
