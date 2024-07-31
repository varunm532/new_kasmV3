from flask_restful import Resource
import os
from dotenv import load_dotenv
import requests
from api.jwt_authorize import token_required
from model.user import User

class GitHubUser(Resource):
    @token_required
    def get(self, uid):
        # Load environment variables
        load_dotenv()
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        # Validate UID and get user data from GitHub API
        try:
            url = f'https://api.github.com/user/{uid}'
            headers = {'Authorization': f'token {github_token}'}
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                return {'message': 'Invalid UID'}, 404
            elif response.status_code != 200:
                return {'message': 'Failed to fetch user data'}, response.status_code

            user_data = response.json()
            email = user_data.get('email')

            if not email:
                return {'message': 'Email not available for this user'}, 404

            return {'email': email}, 200

        except Exception as e:
            return {'message': str(e)}, 500
