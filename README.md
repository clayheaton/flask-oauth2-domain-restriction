### Example Flask app authenticating to Google and restricting to a domain

This is a simple Flask app showing how to integrate [oauth2client](https://oauth2client.readthedocs.io/en/latest/index.html) for authentication with Google and restrict logins to a specified domain.

Note that the [UserOAuth2](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.flask_util.html#oauth2client.contrib.flask_util.UserOAuth2) storage retains credentials during the [`callback_view()`](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.flask_util.html#oauth2client.contrib.flask_util.UserOAuth2.callback_view) method. This means that the data of users who are not authorized due to a domain mismatch is still stored by the `oauth2client` library. 

One user [forked the oauth2client library](https://github.com/google/oauth2client/issues/677#issuecomment-262074257) to override the `callback_view()` method to prevent that. One of the library authors suggested that [he is unlikely](https://github.com/google/oauth2client/issues/677#issuecomment-290448996) to add new features to the library. 

This example recognizes that problem and accepts it, opting to reject users in the `_request_user_info()` function instead of through a fork of the library. In other words, the app tries to authenticate with Google, the response from Google is "ok." We then look at the domain name on the authenticated email address and reject it in the callback function associated with the OAuth session. 

### Using a modified version of the oauth2client library

To reject prior to storing the credentials, you have to use a fork of the oauth2client that compares a keyword argument with key `hd` sent to the flow with the `hd` value on the `credentials.id_token`, as referenced in the note above. If you are interested in that approach, [here's the link to a fork of the oauth2client library](https://github.com/clayheaton/oauth2client). The necessary change is in the [`flack_util.py`](https://github.com/clayheaton/oauth2client/blob/master/oauth2client/contrib/flask_util.py) file around [line 424](https://github.com/clayheaton/oauth2client/blob/master/oauth2client/contrib/flask_util.py#L424). When you init the app, you send the extra `hd` argument, which enters the `flow_kwargs` of the oauth2 object:

```
oauth2.init_app(
    app,
    scopes=['email', 'profile'],
    authorize_callback=_request_user_info,
    hd='thealloweddomain.com')
``` 

In that case, you can simplify the `_request_user_info()` function in `app.py` to remove the post-authentication check.

----

This is a highly modified version of Google's [Python Bookshelf App](https://cloud.google.com/python/getting-started/tutorial-app) example. I stripped out most features, functions, etc. that are not necessary to understand how to use oauth2client. 

For security reasons, you should fork the oauth2client library and make the change yourself. You can then install your modified version of the library easily with pip as such:

```
pip install --upgrade https://github.com/yourgithubaccount/oauth2client/tarball/master
```

----

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.