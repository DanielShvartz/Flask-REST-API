import os
import requests
from dotenv import load_dotenv
import jinja2

# The background worker is a seperate from the flask app, so it needs to load the .env file.

load_dotenv()

domain = os.getenv("MAILGUN_API_DOMAIN")
api_key = os.getenv("MAILGUN_API_KEY")

template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)

def send_simple_message(to, subject, body, html):
    
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={"from": f"Daniel Shvartz <mailgun@{domain}>",
              "to": [to],
              "subject": subject,
              "text": body,
              "html": html})

def send_user_registration_email(email, username):
    # we also added this function which sends calls the sending email function and adds app body subject etc.
    response = send_simple_message(to = email,
                                   subject = "Successfully Signed Up",
                                   body = f"Hello {username} - Welcome To The REST API", 
                                   html=render_template("email/action.html", username=username))
    print('Sent email and response: ', response)

    
    # render template will call the action.html page and can pass the username as a variable.
    # rending means getting the context within the context, and it can pass the variable given.