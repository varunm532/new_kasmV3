from flask import Blueprint, request, g
from flask_restful import Api, Resource
import base64
from model.users import User
from __init__ import db
from auth_middleware import token_required

pfp_api = Blueprint('pfp_api', __name__, url_prefix='/api/pfp')
api = Api(pfp_api)

# Resource: uploading profile picture/image
class _UploadPFP(Resource):
    def post(self):
        # Check if file part is in request
        if 'file' not in request.files:
            return {'message': 'Please upload an image first'}, 400
        file = request.files['file'] # Retrieve file from request
        # Ensure file selected for upload
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        
        user_uid = request.form.get('uid') # get user UID from form data
        user = User.query.filter_by(_uid=user_uid).first() # Find user by UID
        if user:
            # File conversion/reading
            img_data = file.read()  # Read image data from provided/inputted file
            base64_encoded = base64.b64encode(img_data).decode('utf-8')  # Encode image data as base64
            user._pfp = base64_encoded  # Update profile picture data
            db.session.commit()  # Commit changes to database
            return {'message': 'Profile picture updated successfully'}, 200
        else:
            return {'message': 'User not found'}, 404

class _GetPFP(Resource):
    def get(self):
        # Get UID from request arguments
        user_uid = request.args.get('uid')

        # Check if UID exists
        if not user_uid:
            return {'message': 'UID required.'}, 400

        # Query database for user by UID
        user = User.query.filter_by(_uid=user_uid).first()

        # If user exists and has profile picture, return profile picture data
        if user and user._pfp:
            return {'pfp': user._pfp}, 200
        
api.add_resource(_UploadPFP, '/upload-pfp')
api.add_resource(_GetPFP, '/get-pfp')