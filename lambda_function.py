from __future__ import print_function

import json
import urllib
import urllib2
import boto3
import os
import base64

s3 = boto3.client('s3')

API_URL = 'https://api_demo.hybrik.com/v1'
COMPLIANCE_DATE = '20180501'
INPUT_FOLDER_NAME = 'lambda-watchfolder-inputs/'
S3_OUTPUT_BASE_URL = 's3://hybrik-demo-bucket/lambda_watchfolder_outputs/'

# Decrypt credentials
OAPI_KEY = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(os.environ['oapi_key']))['Plaintext']
OAPI_SECRET = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(os.environ['oapi_secret']))['Plaintext']
USERNAME = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(os.environ['username']))['Plaintext']
PASSWORD = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(os.environ['password']))['Plaintext']

def getHybrikAuthToken():
    base64string = base64.encodestring('%s:%s' % (OAPI_KEY, OAPI_SECRET)).replace('\n', '')
    headers = {
        'X-Hybrik-Compliance': COMPLIANCE_DATE,
        'Content-Type': 'application/json',
        'Authorization': 'Basic %s' % base64string
    }

    data = {
        "auth_key": USERNAME,
        "auth_secret": PASSWORD
    }

    try:        
        # Send auth request
        data = json.dumps(data)
        request = urllib2.Request(API_URL + '/login', data, headers)
        response = urllib2.urlopen(request)
            
        # Return token
        payload = json.loads(response.read())
        return payload['token']

    except Exception as e:
        print(e)
        print('Error retrieving auth token.')
        raise e



def lambda_handler(event, context):

    # Get the bucket name
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    
    # Get object key and convert pluses
    input_key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    auth_token = getHybrikAuthToken()
    base64string = base64.encodestring('%s:%s' % (OAPI_KEY, OAPI_SECRET)).replace('\n', '')

    # Headers for job submission request
    headers = {
        'X-Hybrik-Compliance': '20180501',
        'X-Hybrik-Sapiauth': auth_token,
        'Content-Type': 'application/json',
        'Authorization': 'Basic %s' % base64string
    }
    
    # Hybrik job data
    api_data = {
      "definitions": {
        "profile_name": "transmux_mov_to_mp4",
        "category": "transmuxing",
        "source": "s3://" + input_bucket + "/" + input_key,
        "destination": S3_OUTPUT_BASE_URL
      },
      "name": "{{profile_name}}:  {{source}}",
      "payload": {
        "elements": [
          {
            "uid": "source_file",
            "kind": "source",
            "payload": {
              "kind": "asset_url",
              "payload": {
                "storage_provider": "s3",
                "url": "{{source}}"
              }
            }
          },
          {
            "uid": "transmux",
            "kind": "transcode",
            "payload": {
              "location": {
                "storage_provider": "s3",
                "path": "{{destination}}"
              },
              "targets": [
                {
                  "file_pattern":  "{source_basename}{default_extension}",
                  "existing_files": "replace",
                  "container": {
                    "kind": "mp4"
                  },
                  "video": {
                    "codec": "copy"
                  },
                  "audio": [
                    {
                      "codec": "copy"
                    }
                  ]
                }
              ]
            }
          }
        ],
        "connections": [
          {
            "from": [
              {
                "element": "source_file"
              }
            ],
            "to": {
              "success": [
                {
                  "element": "transmux"
                }
              ]
            }
          }
        ]
      }
    }

    try:        
        # Send request to Hybrik API
        data = json.dumps(api_data)
        request = urllib2.Request(API_URL + '/jobs', data, headers)
        response = urllib2.urlopen(request)
        
        # Log the response
        print("API RESPONSE:")
        print(response.read())

    except Exception as e:
        print(e)
        print('Error submitting job for {} from S3 bucket {}.'.format(input_key, input_bucket))
        raise e