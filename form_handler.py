import json
import boto3
from os import environ
from hashlib import sha256

s3 = boto3.resource('s3')
bucket = s3.Bucket(environ["S3_BUCKET_NAME"])

def lambda_handler(event, context):
    # TODO implement
    print(event)
    print(context)
    if event["requestContext"]["http"]["method"] == "POST":
        data = json.dumps(event).encode("utf8")
        sha = sha256(data).hexdigest() + ".json"
        bucket.put_object(Body=data, Key=sha)
        return {
            'statusCode': 200,
            'headers': {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Headers': "Content-Type",
              'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                "success": True
            })
        }
    elif event["requestContext"]["http"]["method"] == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Headers': "Content-Type",
              'Access-Control-Allow-Methods': 'OPTIONS,POST'
            }
        }
    else:
        return {
            'statusCode': 400,
            'headers': {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Headers': "Content-Type",
              'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                "success": False
            })
        }
