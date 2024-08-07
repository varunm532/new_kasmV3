from flask_restful import Resource
from datetime import datetime
import requests
from __init__ import app

class GitHubUser(Resource):
    def get(self, uid):
        url = app.config['GITHUB_API_URL'] + f'/users/{uid}'
        token = app.config['GITHUB_TOKEN']
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

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
    
    def get_profile_links(self, uid):
        user_data, status_code = self.get(uid)
        if status_code != 200:
            return user_data, status_code
        
        profile_links = {
            'profile_url': user_data.get('html_url'),
            'repos_url': user_data.get('repos_url')
        }
        return profile_links, 200

    def get_commit_stats(self, uid, start_date_str, end_date_str):
        url = "https://api.github.com/graphql" 
        token = app.config['GITHUB_TOKEN']
        # Convert to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Convert to ISO 8601 format
        start_date_iso = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_iso = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        query = """
        query($login: String!, $from: DateTime!, $to: DateTime!) {
            user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                    totalCommitContributions
                }
            }
        }
        # ten_days_before_now = (datetime.utcnow() - timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%SZ')
        """
        variables = {
            "login": uid,
            "from": start_date_iso,
            "to": end_date_iso
        }
        try:
            headers = {'Authorization': f'bearer {token}'}
            response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

            if response.status_code != 200:
                return {'message': 'GitHub API failed to fetch commit stats'}, response.status_code

            data = response.json()
            commit_stats = data['data']['user']['contributionsCollection']['totalCommitContributions']
            return {'total_commit_contributions': commit_stats}, 200

        except Exception as e:
            return {'message': str(e)}, 500


class GitHubOrg(Resource):
    def get_users(self, org_name):
        url = app.config['GITHUB_API_URL'] + f'/orgs/{org_name}/members'
        token = app.config['GITHUB_TOKEN']
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {'message': 'GitHub API failed to fetch organization members'}, response.status_code

            return response.json(), 200

        except Exception as e:
            return {'message': str(e)}, 500

    def get_repos(self, org_name):
        url = app.config['GITHUB_API_URL'] + f'/orgs/{org_name}/repos'
        token = app.config['GITHUB_TOKEN']
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {'message': 'GitHub API failed to fetch organization repositories'}, response.status_code

            return response.json(), 200

        except Exception as e:
            return {'message': str(e)}, 500
