from flask import Flask, render_template, request, redirect, make_response
import requests
import base64
import os
import json

import binascii
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

def urlsafe_b64decode(data):
    data = str.encode(data)
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    return base64.urlsafe_b64decode(data)

def unpack(cipher_text):
  # [iv-len:1][iv-bytes][aad-len:2][aad-bytes][cipher-len:4][cipher-bytes][tag-bytes:16]
  # import pdb; pdb.set_trace()
  iv_aad_cipher_text_auth_tag = cipher_text # binascii.hexlify()
  # Extract iv
  iv_length = iv_aad_cipher_text_auth_tag[0]
  iv = iv_aad_cipher_text_auth_tag[1:(iv_length + 1)]
  # Extract aad
  aad_cipher_text_auth_tag = iv_aad_cipher_text_auth_tag[(iv_length+1):]
  aad_length = aad_cipher_text_auth_tag[0] + (aad_cipher_text_auth_tag[1] << 8)
  aad = b''
  if aad_length > 0:
      aad = aad_cipher_text_auth_tag[2:(aad_length + 2)]
  # Extract the auth_tag. auth_tag_length = 16.
  cipher_text_with_auth_tag = aad_cipher_text_auth_tag[(aad_length + 2):]
  cipher_text = cipher_text_with_auth_tag[4:-16]
  tag = cipher_text_with_auth_tag[-16:]
  return iv, aad, cipher_text, tag

def decrypt(context, secret):
  key = hashlib.sha256(secret.encode('utf-8')).digest()
  iv, aad, cipher_text, tag = unpack(context);
  cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
  if len(aad) > 0:
      cipher.update(aad)
  cipher.update(aad)
  data = cipher.decrypt_and_verify(cipher_text, tag)
  return data


app = Flask(__name__)

def get_deeplink(access_token):
    deeplink_api_url = 'https://api.zoom.us/v2/zoomapp/deeplink/'
    data = json.dumps({'action': 'go'})
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json' }
    res = requests.post(deeplink_api_url, data=data, headers=headers)
    return json.loads(res.text)

@app.route('/')
def start():
    clientSecret = os.environ.get('CLIENT_SECRET')

    cipher_text = urlsafe_b64decode(b64_cipher_context)
    data_json = decrypt(cipher_text, clientSecret)
    data_obj = json.loads(data_json)
    res = make_response(render_template('index.html'), data=data_obj)
    res.headers['Referrer-Policy'] = 'same-origin'
    res.headers['crossOriginEmbedderPolicy'] = False
    res.headers['Strict-Transport-Security'] = 'max-age=31536000'
    res.headers['X-Content-Type-Options'] = 'nosniff'
    res.headers['Content-Security-Policy'] = "default-src 'self'; styleSrc 'self'; scriptSrc 'self'; imgSrc 'self'; connect-src 'self'; base-uri 'self'; form-action 'self'"
    return res

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