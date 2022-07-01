from flask import Flask, render_template, request
import requests
import base64
import os

app = Flask(__name__)
@app.route('/')
def start():
    return render_template("index.html")

@app.route("/redirect")
def oauth_redirect():
    clientID= os.environ.get('CLIENT_ID', '')
    clientSecret = os.environ.get('CLIENT_SECRET','')
    client_secret_combined = clientID + ":" + clientSecret
    client_secret_combined_bytes = client_secret_combined.encode('ascii')
    client_secret_combined_bytes = base64.b64encode(client_secret_combined_bytes)
    client_secret_combined_str = client_secret_combined_bytes.decode('ascii')
    code = request.args.get('code', None)
    data = {'code': code, 'grant_type': 'authorization_code', 'redirect_uri': 'https://7zljzja270.execute-api.us-west-1.amazonaws.com/me'}
    headers = {'Authorization': client_secret_combined_str }
    res = requests.post('https://zoom.us/oauth/token', data=data, headers=headers)
    if res.status_code == 200:
        access_token_data = res.json()
        return render_template("debug.html", data=access_token_data)
    else:
        debug = res.json()
        debug['env'] = os.enviorn
        return render_template("debug.html", data=debug)


app.run()