"""
Flask Documentation:     http://flask.pocoo.org/docs/
Flask-SQLAlchemy Documentation: http://flask-sqlalchemy.pocoo.org/
SQLAlchemy Documentation: http://docs.sqlalchemy.org/
FB Messenger Platform docs: https://developers.facebook.com/docs/messenger-platform.

This file creates your application.
"""

import os
import random
import flask
import requests
from flask_sqlalchemy import SQLAlchemy
from wit import Wit

FACEBOOK_API_MESSAGE_SEND_URL = (
    'https://graph.facebook.com/v2.6/me/messages?access_token=%s')

app = flask.Flask(__name__)

# TODO: Set environment variables appropriately.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['FACEBOOK_PAGE_ACCESS_TOKEN'] = os.environ[
    'FACEBOOK_PAGE_ACCESS_TOKEN']
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')
app.config['FACEBOOK_WEBHOOK_VERIFY_TOKEN'] = 'mysecretverifytoken'


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Free form address for simplicity.
    full_address = db.Column(db.String, nullable=False)

    # Connect each address to exactly one user.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    # This adds an attribute 'user' to each address, and an attribute
    # 'addresses' (containing a list of addresses) to each user.
    user = db.relationship('User', backref='addresses')


@app.route('/')
def index():
    """Simple example handler.

    This is just an example handler that demonstrates the basics of SQLAlchemy,
    relationships, and template rendering in Flask.

    """
    # Just for demonstration purposes
    for user in User.query:  #
        print 'User %d, username %s' % (user.id, user.username)
        for address in user.addresses:
            print 'Address %d, full_address %s' % (
                address.id, address.full_address)

    # Render all of this into an HTML template and return it. We use
    # User.query.all() to obtain a list of all users, rather than an
    # iterator. This isn't strictly necessary, but just to illustrate that both
    # User.query and User.query.all() are both possible options to iterate over
    # query results.
    client = Wit("HFCPSWOKZXNXJ6W4M7LIP7RHAHWBN63Q")
    
    return flask.render_template('index.html', users=User.query.all())


@app.route('/fb_webhook', methods=['GET', 'POST'])
def fb_webhook():
    greetings = ['hai', 'hello', 'howdy', 'wassup', 'hallo', 'hiii','hey','hi']
    a = "Never underestimate the power of hard work"
    b = "Focus and Hardwork can get you places"
    c = "Winners don't make excuses. You are one of them"
    d = "Believe in yourself. You can do it"
    quotes = [a,b,c,d]
    e= "You should listen to Taylor swift's shake it off. My personal favorite"
    f = "How about reading something good ? Try https://zenhabits.net/"
    g= "You are a fighter."
    h ="Something I like. You might too, https://www.youtube.com/watch?v=GdmMkpm2MU8 "
    i ="Listen to me, read this  https://www.enkiverywell.com/happy-thoughts.html"
    j = "Watch this. It will help you. https://www.youtube.com/watch?v=zCyB2DQFdA0"
    k = "Something I like. You might too, https://www.youtube.com/watch?v=GdmMkpm2MU8 "
    notthat = [e,f,g,h, i, j, k]
    """This handler deals with incoming Facebook Messages.

    In this example implementation, we handle the initial handshake mechanism,
    then just echo all incoming messages back to the sender. Not exactly Skynet
    level AI, but we had to keep it short...

    """

    # Handle the initial handshake request.
    if flask.request.method == 'GET':
        if (flask.request.args.get('hub.mode') == 'subscribe' and
            flask.request.args.get('hub.verify_token') ==
            app.config['FACEBOOK_WEBHOOK_VERIFY_TOKEN']):
            challenge = flask.request.args.get('hub.challenge')
            return challenge
        else:
            print 'Received invalid GET request'
            return ''  # Still return a 200, otherwise FB gets upset.

    # Get the request body as a dict, parsed from JSON.
    payload = flask.request.json

   
    # TODO: Validate app ID and other parts of the payload to make sure we're
    # not accidentally processing data that wasn't intended for us.

    # Handle an incoming message.
    # TODO: Improve error handling in case of unexpected payloads.
    for entry in payload['entry']:
        for event in entry['messaging']:
            if 'message' not in event:
                continue
            message = event['message']
            # Ignore messages sent by us.
            if message.get('is_echo', False):
                continue
            # Ignore messages with non-text content.
            if 'text' not in message:
                continue
            sender_id = event['sender']['id']
            client = Wit("HFCPSWOKZXNXJ6W4M7LIP7RHAHWBN63Q")
            resp = client.message(str(message['text']))
            entity = None
            value = None
            try:
                entity = list(resp['entities'])[0]
                print entity
                value = resp['entities'][entity][0]['value']
                print value
            except:
                pass
            if str(message['text']).lower() in greetings:
                message_text = random.choice(greetings)
            elif entity == "emotion":
                message_text =  "Oh why do you feel {}".format(str(value))+ " don't worry. This too shall pass. Arlie knows you are awesome"
            elif entity =="motivation" :
                 message_text = "Your good friend Arlie is here to  {} you".format(str(value)) +"\n"+ random.choice(quotes)
            elif entity == "quotes":
                message_text = random.choice(quotes)
            elif entity== "red":
                message_text = "Oh dear, listen to me. Call 1-800-273-8255 immediately. This is not the end dear."
            elif entity=="bye" or  entity =="thanks":
                message_text ="Anytime!"
            elif entity =="notthat":
                message_text="Oh don't say that. "+ random.choice(notthat)
            else:
                 message_text = "Hmm , I couldn't get that, but always remember that you are awesome."

            request_url = FACEBOOK_API_MESSAGE_SEND_URL % (
                app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
            requests.post(request_url,
                          headers={'Content-Type': 'application/json'},
                          json={'recipient': {'id': sender_id},
                                'message': {'text': message_text}})

    # Return an empty response.
    return ''

if __name__ == '__main__':
    app.run(debug=True)
