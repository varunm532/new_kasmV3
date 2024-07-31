from flask_restful import Resource
import requests
from __init__ import app

class GitHubUser(Resource):
    def get(self, uid):
        url = app.config['GITHUB_API_URL'] + f'/user/{uid}'
        token = app.config['GITHUB_TOKEN']
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        # Validate UID and get user data from GitHub API
        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                return {'message': f'Invalid UID {uid}'}, 404
            elif response.status_code != 200:
                return {'message': 'GitHub API failed to fetch user data'}, response.status_code

            return response.json(), 200

        except Exception as e:
            return {'message': str(e)}, 500