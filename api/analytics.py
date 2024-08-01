from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from model.github import GitHubUser

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

api.add_resource(GitHubUserAPI, '/github/user/<string:uid>')

if __name__ == '__main__':
    from __init__ import app
    app.register_blueprint(analytics_api)
    app.run(debug=True)
