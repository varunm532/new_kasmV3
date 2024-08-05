from flask_restful import Resource
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

    def get_commit_stats(self, uid, start_date, end_date):
        url = app.config['GITHUB_API_GRAPHQL_URL']
        token = app.config['GITHUB_TOKEN']
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
        """
        variables = {
            "login": uid,
            "from": start_date,
            "to": end_date
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
