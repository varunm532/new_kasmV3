from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from model.github import GitHubUser, GitHubOrg

analytics_api = Blueprint('analytics_api', __name__, url_prefix='/api/analytics')
api = Api(analytics_api)

class GitHubUserAPI(Resource):
    def get(self, uid):
        try:
            github_user_resource = GitHubUser()
            response = github_user_resource.get(uid)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserProfileLinks(Resource):
    def get(self, uid):
        try:
            github_user_resource = GitHubUser()
            response = github_user_resource.get_profile_links(uid)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserCommits(Resource):
    def get(self, uid):
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            if not start_date or not end_date:
                return {'message': 'start_date and end_date parameters are required'}, 400

            github_user_resource = GitHubUser()
            response = github_user_resource.get_commit_stats(uid, start_date, end_date)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class GitHubOrgUsers(Resource):
    def get(self, org_name):
        try:
            github_org_resource = GitHubOrg()
            response = github_org_resource.get_users(org_name)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class GitHubOrgRepos(Resource):
    def get(self, org_name):
        try:
            github_org_resource = GitHubOrg()
            response = github_org_resource.get_repos(org_name)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

api.add_resource(GitHubUserAPI, '/github/user/<string:uid>')
api.add_resource(UserProfileLinks, '/github/user/<string:uid>/profile_links')
api.add_resource(UserCommits, '/github/user/<string:uid>/commits')
api.add_resource(GitHubOrgUsers, '/github/org/<string:org_name>/users')
api.add_resource(GitHubOrgRepos, '/github/org/<string:org_name>/repos')

if __name__ == '__main__':
    from __init__ import app
    app.register_blueprint(analytics_api)
    app.run(debug=True)
