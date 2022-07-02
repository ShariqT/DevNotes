from flask import Flask, render_template, request, redirect
import requests
import base64
import os
import json

app = Flask(__name__)

def get_deeplink(access_token):
    deeplink_api_url = 'https://api.zoom.us/v2/zoomapp/deeplink/'
    data = json.dumps({'action': 'go'})
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json' }
    res = requests.post(deeplink_api_url, data=data, headers=headers)
    return res.text

@app.route('/')
def start():
    return render_template("index.html")

@app.route("/redirect")
def oauth_redirect():
    clientID = os.environ.get('CLIENT_ID')
    clientSecret = os.environ.get('CLIENT_SECRET')
    client_secret_combined = clientID + ":" + clientSecret
    client_secret_combined_bytes = client_secret_combined.encode('ascii')
    client_secret_combined_bytes = base64.b64encode(client_secret_combined_bytes)
    client_secret_combined_str = client_secret_combined_bytes.decode('ascii')
    code = request.args.get('code', None)
    data = {'code': code, 'grant_type': 'authorization_code', 'redirect_uri': 'https://7zljzja270.execute-api.us-west-1.amazonaws.com/redirect'}
    headers = {'Authorization': "Basic " + client_secret_combined_str }
    res = requests.post('https://zoom.us/oauth/token', data=data, headers=headers)
    if res.status_code == 200:
        access_token_data = res.json()
        deeplink = get_deeplink(access_token_data['access_token'])
        # return render_template("debug.html", data=deeplink)
        return render_template("go.html", data=deeplink)
    else:
        debug = res.json()
        debug['env'] = os.environ
        debug['client_secret_combined'] = client_secret_combined
        return render_template("debug.html", data=debug)


app.run()