## requirements.txt
# Flask==0.10.1
# itsdangerous==0.24
# Jinja2==2.8
# MarkupSafe==0.23
# Werkzeug==0.11.9
# requests

import os

from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify
import requests
import json
import hmac
import hashlib

WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
CIRCLE_API_USER_TOKEN = os.getenv('CIRCLE_API_USER_TOKEN')
CIRCLE_DEPLOY_JOB = os.getenv('CIRCLE_DEPLOY_JOB')
CIRCLE_REMOVE_JOB = os.getenv('CIRCLE_REMOVE_JOB')

def temp_token():
    import binascii
    temp_token = binascii.hexlify(os.urandom(24))
    return temp_token.decode('utf-8')

def pr_action(request_json):

    if 'action' in request_json and 'number' in request_json:
        pr_action_list = ['opened', 'reopened', 'synchronize']
        pr_action = request_json['action']
        pr_number = request_json['number']
        pr_branch = request_json['pull_request']['head']['ref']
        repo_full_name = request_json['pull_request']['head']['repo']['full_name']
        if pr_action in pr_action_list:
            if deploy_review(pr_number, pr_branch, repo_full_name):
                return True
        elif pr_action == 'closed':
            if remove_review(pr_number, pr_branch, repo_full_name):
                return True

def deploy_review(pr_number, pr_branch, repo_full_name):
    headers = {
        'Content-Type': 'application/json',
        'Circle-Token': '{}'.format(CIRCLE_API_USER_TOKEN)
    }
    payload = {
        "build_parameters": {
            "CIRCLE_JOB": CIRCLE_DEPLOY_JOB,
            "PR_NUMBER": pr_number,
            "PR_BRANCH": pr_branch
        }
    }
    url = "https://circleci.com/api/v1.1/project/github"
    request_url = '{}/{}/tree/{}'.format(url,repo_full_name,pr_branch)
    response = requests.post(request_url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        return True


def remove_review(pr_number, pr_branch, repo_full_name):
    headers = {
        'Content-Type': 'application/json',
        'Circle-Token': '{}'.format(CIRCLE_API_USER_TOKEN)
    }
    payload = {
        "build_parameters": {
            "CIRCLE_JOB": CIRCLE_REMOVE_JOB,
            "PR_NUMBER": pr_number,
            "PR_BRANCH": pr_branch
        }
    }
    url = "https://circleci.com/api/v1.1/project/github"
    request_url = '{}/{}/tree/{}'.format(url,repo_full_name,pr_branch)
    response = requests.post(request_url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        return True

app = Flask(__name__)

authorised_clients = {}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    request_json = request.json
    if request.method == 'GET':
        return jsonify({'status':'success'}), 200

    elif request.method == 'POST':
        key = bytes(WEBHOOK_VERIFY_TOKEN, 'utf-8')
        expected_signature = hmac.new(key=key, msg=request.data, digestmod=hashlib.sha1).hexdigest()
        incoming_signature = request.headers.get('X-Hub-Signature').split('sha1=')[-1].strip()
        if not hmac.compare_digest(incoming_signature, expected_signature):
            return jsonify({'status':'not authorised'}), 401
        else:
            if pr_action(request_json):
                response_json = {'status': 'success'}
                return jsonify(response_json), 200,
            elif request.headers.get('X-GitHub-Event') == 'ping':
                response_json = {'status': 'success'}
                return jsonify(response_json), 200,
            else:
                response_json = {'status': 'failed'}
                return jsonify(response_json), 500, 
    else:
        abort(400)

if __name__ == '__main__':
    if WEBHOOK_VERIFY_TOKEN is None:
        print('WEBHOOK_VERIFY_TOKEN has not been set in the environment.\nGenerating random token...')
        token = temp_token()
        print('Token: %s' % token)
        WEBHOOK_VERIFY_TOKEN = token
    app.run(host='0.0.0.0', debug=True)
