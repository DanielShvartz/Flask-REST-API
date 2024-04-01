import os
import requests
from dotenv import load_dotenv

# The background worker is a seperate from the flask app, so it needs to load the .env file.

load_dotenv()

domain = os.getenv("MAILGUN_API_DOMAIN")
api_key = os.getenv("MAILGUN_API_KEY")

def send_simple_message(to, subject, body):
    
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={"from": f"Daniel Shvartz <mailgun@{domain}>",
              "to": [to],
              "subject": subject,
              "text": body})

def send_user_registration_email(email, username):
    # we also added this function which sends calls the sending email function and adds app body subject etc.
    response = send_simple_message(to = email,
                                   subject = "Successfully Signed Up",
                                   body = f"Hello {username} - Welcome To The REST API")
    print('Sent email and response: ', response)
    return response
