import os
import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode

AUTH_API = os.environ['AUTH_API']
# get client id from env variable
client_id = os.environ['CLIENT_ID']

def lambda_handler(event, context):
    # get auth code from query string
    code = event['queryStringParameters'].get('code')
    if not code:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Code is required"})
        }

    # print event to logs
    print(event)

    # call cognito token endpoint to ecchange code for tokens
    token_url = 'https://' + AUTH_API + '/oauth2/token'

    # redirect URI is this function's API gateway URL
    redirect_uri = 'https://' + event['headers']['host'] + '/auth/callback'

    payload = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'code': code,
        'redirect_uri': redirect_uri
    }

    print(payload)

    # make a POST request to token endpoint using urllib
    req = Request(token_url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, method='POST', data=urlencode(payload).encode("utf-8"))
    response = urlopen(req)

    # decode response
    response = json.loads(response.read())

    # print response to logs
    print(response)

    # return an HTTP page with the refresh token
    body = """
    <html><body>
        <h1>Success!</h1>
        <p>This page will redirect you to the app with the refresh token in <span id="countdown">5</span> seconds.</p>
        <p>If you are not redirected, click <a href="javascript:redirect()">here</a> or copy the refresh token below.</p>
        <textarea rows="10" cols="100">{}</textarea>
        <!-- Add a function to redirect to the app with the refresh token -->
        <script>
        function redirect() {{
            window.location.href = 'http://localhost:3000?refresh_token={}'
        }}

        // count down from 5 to 0
        var seconds = 5;
        function countdown() {{
            seconds = seconds - 1;
            if (seconds < 0) {{
                // redirect to the app
                redirect();
            }} else {{
                // update the countdown
                document.getElementById("countdown").innerHTML = seconds;
                // call this function again after 1 second
                setTimeout(countdown, 1000);
            }}
        }}

        // start the countdown
        countdown();
        </script>
    </body></html>
    """.format(response['refresh_token'], response['refresh_token'])
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': body
    }
