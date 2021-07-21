import json
import boto3
from os import environ
import pprint
import urllib.request

ses = boto3.client('ses')

s3 = boto3.resource('s3')
bucket = s3.Bucket(environ["S3_BUCKET_NAME"])

WELCOME_MAILER_ADDRESS = environ["WELCOME_MAILER_ADDRESS"]
NOTIFY_MAILER_ADDRESS = environ["NOTIFY_MAILER_ADDRESS"]

def notify(obj, body):
    ses.send_email(
        Source=f"Couchers.org <{NOTIFY_MAILER_ADDRESS}>",
        Destination={
            "ToAddresses": [
                "Aapeli <redacted@example.com>",
                "Itsi <redacted@example.com>"
            ]
        },
        Message={
            'Subject': {
                'Data': 'New sign up',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data':
f"""Someone new signed up:

Name: {body.get("name", "missing")}
Email: {body.get("email", "missing")}
Username: {body.get("username", "missing")}
Wants to contribute to: {body.get("contribute", "missing")}

* Age
{body.get("age", "missing")}

* Gender
{body.get("gender", "missing")}

* Country and city
{body.get("location", "missing")}

* What kinds of expertise do you have that could help us build and grow this platform?
{body.get("expertise", "missing")}

* Briefly describe your experience as a couch-surfer.
{body.get("experience", "missing")}

* Please share any ideas you have that would improve the couch-surfing experience for you and for the community.
{body.get("ideas", "missing")}

* What feature would you like implemented first, and why? How could we make that feature as good as possible for your particular use?
{body.get("features", "missing")}



Submitted data:
{pprint.pformat(body)}


Full data:
{pprint.pformat(obj)}
""",
                    'Charset': 'UTF-8'
                }
            }
        }
    )

def ticket(obj, body):
    ses.send_email(
        Source=f"Couchers.org <{NOTIFY_MAILER_ADDRESS}>",
        Destination={
            "ToAddresses": [
                "Couchers <redacted@example.com>"
            ]
        },
        Message={
            'Subject': {
                'Data': 'New sign up',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data':
f"""Name: {body.get("name", "missing")}
Email: {body.get("email", "missing")}
Username: {body.get("username", "missing")}
Wants to contribute to: {body.get("contribute", "missing")}

* Age
{body.get("age", "missing")}

* Gender
{body.get("gender", "missing")}

* Country and city
{body.get("location", "missing")}

* What kinds of expertise do you have that could help us build and grow this platform?
{body.get("expertise", "missing")}

* Briefly describe your experience as a couch-surfer.
{body.get("experience", "missing")}

* Please share any ideas you have that would improve the couch-surfing experience for you and for the community.
{body.get("ideas", "missing")}

* What feature would you like implemented first, and why? How could we make that feature as good as possible for your particular use?
{body.get("features", "missing")}
""",
                    'Charset': 'UTF-8'
                }
            }
        }
    )

def welcome_email(name, email):
    ses.send_email(
        Source=f"Couchers.org <{WELCOME_MAILER_ADDRESS}>",
        Destination={
            "ToAddresses": [
                email
            ]
        },
        Message={
            'Subject': {
                'Data': 'Volunteering for Couchers.org',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data':
f"""Hi {name},

Thanks for signing up to become a Couchers.org contributor. It means a lot to us and the whole community that people want to offer their time to give back and help grow this new platform.

We'll read your form and get back to you as soon as possible about how you can volunteer.

To get started, the first things you should do are:

1. Share the link with your trusted couch surfing friends and invite them onto the new platform!
Platform link: https://app.couchers.org

2. Fill out your profile by heading to your user page and editing your profile and home.
Profile link: https://app.couchers.org/user

3. Head over to our community forum to introduce yourself, provide feedback, and get to know other community members and core contributors. You can also join our online events to meet other members of the community face to face, which you can find at the forum as well. Everyone is welcome, so feel free to share the link!
Forum link: https://community.couchers.org

If you are a developer, please start by familiarizing yourself with the code, readme, and development documentation available on GitHub: https://github.com/couchers-org/couchers. Feel free to comment on a good first issue and get started by creating a pull request, and we will get in touch with you quickly to make sure you're supported.

Hope to see you soon!
Emily from the Couchers.org team


———
This email was sent to you because someone (hopefully you) filled out the sign up form on https://app.couchers.org. If it wasn't you, please let us know as soon as possible by emailing us at support@couchers.org.
""",
                    'Charset': 'UTF-8'
                },
                #'Html': {
                #    'Data': 'HTML',
                #    'Charset': 'UTF-8'
                #}
            }
        }
    )

def lambda_handler(event, context):
    for record in event["Records"]:
        key = record["s3"]["object"]["key"]
        print(f"Handling {key}")

        obj = json.loads(bucket.Object(key).get()["Body"].read())
        body = json.loads(obj["body"])

        name = body["name"]
        email = body["email"]

        print(f"{name=}")
        print(f"{email=}")

        # app form doesn't have email yet
        welcome_email(name, email)

        with urllib.request.urlopen("https://hooks.slack.com/services/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", json.dumps({"text": f"{name} just signed up to contribute!"}).encode("utf8")) as f:
            print(f.read().decode('utf-8'))

        notify(obj, body)
        ticket(obj, body)

    return {
        'statusCode': 200,
        'body': json.dumps({"success": True})
    }
