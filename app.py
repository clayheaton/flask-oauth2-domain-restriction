# Further reading
# https://oauth2client.readthedocs.io/en/latest/#oauth2client
# https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.flask_util.html#module-oauth2client.contrib.flask_util

import config # Edit config.py to add your app's credentials.
import json
from flask import current_app, Flask, redirect, session, render_template
import httplib2
from oauth2client.contrib.flask_util import UserOAuth2

oauth2 = UserOAuth2()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initalize the OAuth2 helper.
    oauth2.init_app(
        app,
        scopes=['email', 'profile'],
        authorize_callback=_request_user_info)

    # Add a logout handler.
    @app.route('/logout')
    def logout():
        # Delete the user's profile and the credentials stored by oauth2.
        del session['profile']
        session.modified = True
        oauth2.storage.delete()
        return redirect('/')

    # Add a default root route.
    @app.route("/")
    def index():
        return render_template('index.html')

    return app


def _request_user_info(credentials):
    """
    Makes an HTTP request to the Google+ API to retrieve the user's basic
    profile information, including full name and photo, and stores it in the
    Flask session.
    """
    http = httplib2.Http()

    # User information stored here
    credentials.authorize(http)
    resp, content = http.request('https://www.googleapis.com/plus/v1/people/me')

    if resp.status != 200:
        current_app.logger.error("Error while obtaining user profile: %s" % resp)
        return None

    # Check whether user is authenticating with the allowed domain.
    if (current_app.config['RESTRICT_DOMAIN'] is True and 
        credentials.id_token.get('hd') != current_app.config['REQUIRED_DOMAIN']):

        # Replace with logging for a real app
        print("\n------------------------------------------------------")
        print("User attempted to authenticate with disallowed domain.")
        print("------------------------------------------------------\n")

        # User information deleted here
        oauth2.storage.delete()
        return None

    # Stores the users information in the session profile dictionary
    session['profile'] = json.loads(content.decode('utf-8'))

    # Remove this in production. It's here so you can see what information is stored.
    print("\n------------------------------------------------------")
    print("SESSION PROFILE INFORMATION")
    print("------------------------------------------------------")
    for k,v in session['profile'].items():
        print(k,"--->",v)
    print("------------------------------------------------------\n")


####################

app = create_app(config)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

