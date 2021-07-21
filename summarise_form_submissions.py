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
    form = int(bb.get("form", 3))
    name = bb.get("name", "")
    email = bb.get("email", "")
    contribute = bb.get("contribute", "")

    ideas = None
    features = None
    age = None
    gender = None
    location = None
    cs_experience = None
    develop = None
    expertise = None

    if form != 1:
        ideas = bb.get("ideas", "")
        features = bb.get("features", "")
        age = bb.get("age", "")
        gender = bb.get("gender", "")
        location = bb.get("location", "")
        cs_experience = bb.get("cs_experience", bb.get("experience", ""))
        develop = bb.get("develop", "")
        expertise = bb.get("expertise", "")

    return {"ip": ip, "trace": trace, "request_id": request_id, "user_agent": user_agent, "origin": origin, "time": time, "epoch": epoch, "form": form, "name": name, "email": email, "contribute": contribute, "ideas": ideas, "features": features, "age": age, "gender": gender, "location": location, "cs_experience": cs_experience, "develop": develop, "expertise": expertise, "submission_id": submission_id}

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
                "Data": "Daily summary of responses",
                "Charset": "UTF-8"
            },
            "Body": {
                "Text": {
                    "Data": f"Here's a summary of all the responses we've gotten to the form so far:\n\n<{url}>\n\n\nTo genearte a new report, go to <https://at3fygb9i7.execute-api.us-east-1.amazonaws.com/default/summarise_form_submissions>",
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
        id_ = parsed["name"] + parsed["email"] + parsed["contribute"] + parsed["ip"]
        if id_ in results:
            if parsed["form"] == 2:
                results[id_] = parsed
        else:
            results[id_] = parsed

    results = dict(sorted(results.items()))

    f = io.StringIO()
    fields = ["time", "form", "name", "email", "contribute", "ideas", "features", "age", "gender", "location", "cs_experience", "develop", "expertise", "ip", "trace", "request_id", "user_agent", "origin", "epoch", "submission_id"]
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
