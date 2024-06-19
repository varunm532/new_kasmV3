from flask import Blueprint, request, g
from flask_restful import Api, Resource
import base64
from model.users import User
from __init__ import db
import os
from werkzeug.utils import secure_filename

pfp_api = Blueprint('pfp_api', __name__, url_prefix='/api/pfp')
api = Api(pfp_api)

# Resource: uploading profile picture/image
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class _UploadPFP(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'Please upload an image first'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        
        if not allowed_file(file.filename):
            return {'message': 'File type not allowed'}, 400
        
        user_uid = request.form.get('uid')
        if not user_uid:
            return {'message': 'UID required.'}, 400

        user = User.query.filter_by(_uid=user_uid).first()
        if not user:
            return {'message': 'User not found'}, 404

        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join('instance', filename))  # Save the file to the 'instance' directory
            user._pfp = filename
            db.session.commit()
            return {'message': 'Profile picture updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the profile picture'}, 500

class _GetPFP(Resource):
    def get(self):
        user_uid = request.args.get('uid')
        if not user_uid:
            return {'message': 'UID required.'}, 400

        user = User.query.filter_by(_uid=user_uid).first()
        if not user:
            return {'message': 'User not found'}, 404

        if user._pfp:
            img_path = os.path.join('instance', user._pfp)
            try:
                with open(img_path, 'rb') as img_file:
                    base64_encoded = base64.b64encode(img_file.read()).decode('utf-8')
                    return {'pfp': base64_encoded}, 200
            except FileNotFoundError:
                return {'message': 'Profile picture file not found.'}, 404
        else:
            return {'message': 'Profile picture not set.'}, 404
        
api.add_resource(_UploadPFP, '/upload-pfp')
api.add_resource(_GetPFP, '/get-pfp')