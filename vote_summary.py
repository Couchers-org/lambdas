import json
from os import environ

from hashlib import sha256
import boto3
from csv import DictWriter
import io
ses = boto3.client('ses')

s3 = boto3.resource('s3')
bucket = s3.Bucket(environ["S3_BUCKET_NAME"])
S3_OUTPUT_BUCKET_NAME = environ["S3_OUTPUT_BUCKET_NAME"]
obucket = s3.Bucket(S3_OUTPUT_BUCKET_NAME)

def handle_obj(body, submission_id):
    ip = body["headers"]["x-forwarded-for"]
    trace = body["headers"]["x-amzn-trace-id"]
    request_id = body["requestContext"]["requestId"]
    user_agent = body["headers"]["user-agent"]
    origin = body["headers"]["user-agent"]
    time = body["requestContext"]["time"]
    epoch = body["requestContext"]["timeEpoch"]

    bb = json.loads(body["body"])
    email = bb["email"] if "email" in bb else "<empty>"
    vote = bb["vote"] if "vote" in bb else "<empty>"
    comment = bb["comment"] if "comment" in bb else "<empty>"

    return {"ip": ip, "trace": trace, "request_id": request_id, "user_agent": user_agent, "origin": origin, "time": time, "epoch": epoch, "email": email, "vote": vote, "comment": comment, "submission_id": submission_id}

def notify(url):
    ses.send_email(
        Source=f"Couchers.org <redacted@example.com>",
        Destination={
            "ToAddresses": [
                "Aapeli <redacted@example.com>",
                "Itsi <redacted@example.com>"
            ]
        },
        Message={
            "Subject": {
                "Data": "Vote summary",
                "Charset": "UTF-8"
            },
            "Body": {
                "Text": {
                    "Data": f"Here ya go:\n\n<{url}>\n\n\nTo genearte a new report, go to <https://at3fygb9i7.execute-api.us-east-1.amazonaws.com/vote_summary>",
                    "Charset": "UTF-8"
                }
            }
        }
    )


def lambda_handler(event, context):
    results = {}

    for obj in bucket.objects.all():
        body = json.loads(obj.get()["Body"].read())
        parsed = handle_obj(body, obj.key)
        id_ = parsed["email"] + parsed["ip"] + str(parsed["epoch"])
        results[id_] = parsed

    results = dict(sorted(results.items()))

    f = io.StringIO()
    fields = ["email", "vote", "comment", "time", "ip", "trace", "request_id", "user_agent", "origin", "epoch", "submission_id"]
    writer = DictWriter(f, fieldnames=fields)

    writer.writeheader()
    for id_, row in results.items():
        writer.writerow(row)

    f.seek(0)
    out = f.read()

    data = out.encode("utf8")
    key = sha256(data).hexdigest() + ".csv"
    obucket.put_object(Body=data, Key=key, ACL="public-read")

    notify(f"https://s3.amazonaws.com/{S3_OUTPUT_BUCKET_NAME}/{key}")

    return {
        'statusCode': 200,
        'body': json.dumps({"works": True})
    }
