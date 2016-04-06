from __future__ import print_function

import json
import urllib
import urllib2
import boto3
import os

s3 = boto3.client('s3')

API_URL = 'https://app.zencoder.com/api/v2/jobs'
API_KEY = 'YOUR-ZENCODER-API-KEY'
INPUT_FOLDER_NAME = 'inputs/'
S3_OUTPUT_BASE_URL = 's3://YOUR-S3-BUCKET/outputs/'
NOTIFICATION_EMAIL = 'YOUR-EMAIL-ADDRESS'

def lambda_handler(event, context):

    # Get the bucket name
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    
    # Get object key and convert pluses
    input_key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    # Strip input folder name and file extension from input key to create output key
    input_filename = input_key.replace(INPUT_FOLDER_NAME, '', 1)
    output_key = os.path.splitext(input_filename)[0]

    # Headers for Zencoder request
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Zencoder-Api-Key': API_KEY
    }
    
    # Zencoder API request data
    api_data = {
        "input": "s3://" + input_bucket + "/" + input_key,
        "notifications": NOTIFICATION_EMAIL,
        "output": [
            {
                "audio_bitrate": 64,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "filename": output_key + "-64k.m3u8",
                "format": "aac",
                "public": 1,
                "type": "segmented"
            },
            {
                "audio_bitrate": 56,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "decoder_bitrate_cap": 360,
                "decoder_buffer_size": 840,
                "filename": output_key + "-240k.m3u8",
                "max_frame_rate": 15,
                "public": 1,
                "type": "segmented",
                "video_bitrate": 184,
                "width": 400,
                "format": "ts"
            },
            {
                "audio_bitrate": 56,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "decoder_bitrate_cap": 578,
                "decoder_buffer_size": 1344,
                "filename": output_key + "-440k.m3u8",
                "public": 1,
                "type": "segmented",
                "video_bitrate": 384,
                "width": 400,
                "format": "ts"
            },
            {
                "audio_bitrate": 56,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "decoder_bitrate_cap": 960,
                "decoder_buffer_size": 2240,
                "filename": output_key + "-640k.m3u8",
                "public": 1,
                "type": "segmented",
                "video_bitrate": 584,
                "width": 480,
                "format": "ts"
            },
            {
                "audio_bitrate": 56,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "decoder_bitrate_cap": 1500,
                "decoder_buffer_size": 4000,
                "filename": output_key + "-1040k.m3u8",
                "public": 1,
                "type": "segmented",
                "video_bitrate": 1000,
                "width": 640,
                "format": "ts"
            },
            {
                "audio_bitrate": 56,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "decoder_bitrate_cap": 2310,
                "decoder_buffer_size": 5390,
                "filename": output_key + "-1540k.m3u8",
                "public": 1,
                "type": "segmented",
                "video_bitrate": 1484,
                "width": 960,
                "format": "ts"
            },
            {
                "audio_bitrate": 56,
                "audio_sample_rate": 22050,
                "base_url": S3_OUTPUT_BASE_URL,
                "decoder_bitrate_cap": 3060,
                "decoder_buffer_size": 7140,
                "filename": output_key + "-2040k.m3u8",
                "public": 1,
                "type": "segmented",
                "video_bitrate": 1984,
                "width": 1024,
                "format": "ts"
            },
            {
                "base_url": S3_OUTPUT_BASE_URL,
                "filename": "playlist.m3u8",
                "public": 1,
                "streams": [
                    {
                        "bandwidth": 2040,
                        "path": output_key + "-2040k.m3u8"
                    },
                    {
                        "bandwidth": 1540,
                        "path": output_key + "-1540k.m3u8"
                    },
                    {
                        "bandwidth": 1040,
                        "path": output_key + "-1040k.m3u8"
                    },
                    {
                        "bandwidth": 640,
                        "path": output_key + "-640k.m3u8"
                    },
                    {
                        "bandwidth": 440,
                        "path": output_key + "-440k.m3u8"
                    },
                    {
                        "bandwidth": 240,
                        "path": output_key + "-240k.m3u8"
                    },
                    {
                        "bandwidth": 64,
                        "path": output_key + "-64k.m3u8"
                    }
                ],
                "type": "playlist"
            }
        ]
    }


    try:        
        # Send request to Zencoder API
        data = json.dumps(api_data)
        request = urllib2.Request(API_URL, data, headers)
        response = urllib2.urlopen(request)
        
        # Log the response
        print("API RESPONSE:")
        print(response.read())

    except Exception as e:
        print(e)
        print('Error submitting job for {} from S3 bucket {}.'.format(input_key, input_bucket))
        raise e