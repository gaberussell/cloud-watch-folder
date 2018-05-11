# Watch Folders in the Cloud
#### Automated transcoding using AWS S3, Lambda, and Hybrik
###### *This is the short version of a [more granular walkthrough](https://medium.com/@gaberussell/watch-folders-in-the-cloud-5570713b8726).*

This example shows how to create a cloud-based watch folder. When a new file is added to an [AWS S3](https://aws.amazon.com/s3/) bucket, it will trigger an [AWS Lambda](https://aws.amazon.com/lambda/) function ([lambda_function.py](https://github.com/gaberussell/cloud-watch-folder/blob/master/lambda_function.py)), which makes an API call to start a [Hybrik](https://hybrik.com) transcoding job.

1. Create an S3 Bucket (or use an existing one).
2. Create input and output folders within the bucket (i.e. "inputs/" and "outputs/").
3. Create a new Lambda function and paste the contents of [lambda_function.py](https://github.com/gaberussell/cloud-watch-folder/blob/master/lambda_function.py) into the **Lambda function code** area.
5. Update the global vars at the top:
 * **INPUT_FOLDER_NAME** is the name of the input folder in your S3 bucket
 * **S3_OUTPUT_BASE_URL** includes the output bucket and folder
 * **NOTIFICATION_EMAIL** is an email address where you'd like to receive job notifications (omit [line 39](https://github.com/gaberussell/cloud-watch-folder/blob/master/lambda_function.py#L39) of the function if you don't want notifications)
6. Optionally modify the [output settings](https://github.com/gaberussell/cloud-watch-folder/blob/hybrik/lambda_function.py#L75-L142) to output your preferred formats.
7. Create a new event source for the Lambda function with a source type of **S3**, an event type of **Object Created (all)**, and the prefix will will match the above **INPUT_FOLDER_NAME**.
8. Under **Environment Variables**, check "Enable helpers for encryption in transit." Select a KMS key, or create a new one. Be sure to enable the service role associated with the Lambda function under **Define Key Usage Permissions** within KMS.
Enter the oapi_key, oapi_secret, username, and password as key/values and click "Encrypt" next to each one.

Test by adding video files to the input folder and see that transcoded files populate the output folder. You can troubleshoot errors using Hybrik's job console and the AWS CloudWatch logs for the Lambda function.
 
