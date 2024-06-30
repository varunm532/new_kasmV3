from flask import Blueprint, g, request, current_app as app
from flask_restful import Api, Resource
import base64
from api.auth_middleware import token_required
from model.users import User
from model.pfp import file_upload
from werkzeug.utils import secure_filename
import os

pfp_api = Blueprint('pfp_api', __name__, url_prefix='/api/id')
api = Api(pfp_api)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext.strip('.') for ext in app.config['UPLOAD_EXTENSIONS']]

class _PFP(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'Please upload an image first'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        if not allowed_file(file.filename):
            return {'message': 'File type not allowed'}, 400

        if file.content_length > app.config['MAX_CONTENT_LENGTH']:
            return {'message': 'File size exceeds the allowed limit'}, 400

        user_uid = request.form.get('uid')
        if not user_uid:
            return {'message': 'UID required.'}, 400

        user = User.query.filter_by(_uid=user_uid).first()
        if not user:
            return {'message': 'User not found'}, 404

        if not file_upload(file, user_uid):
            return {'message': 'An error occurred while uploading the profile picture'}, 500
        
        try: 
            user.update(pfp=file.filename)
            return {'message': 'Profile picture updated successfully'}, 200
        except Exception as e:
            return {'message': f'A database error occurred while assigning profile picture: {str(e)}'}, 500

    @token_required()
    def get(self):
        current_user = g.current_user

        if current_user.pfp:
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.uid, current_user.pfp)
            try:
                with open(img_path, 'rb') as img_file:
                    base64_encoded = base64.b64encode(img_file.read()).decode('utf-8')
                    return {'pfp': base64_encoded}, 200
            except FileNotFoundError:
                return {'message': 'Profile picture file not found.'}, 404
        else:
            return {'message': 'Profile picture not set.'}, 404

    @token_required()
    def delete(self):
        current_user = g.current_user

        if current_user.role != 'Admin':
            return {'message': 'Unauthorized.'}, 401

        user_uid = request.args.get('uid')
        if not user_uid:
            return {'message': 'UID required.'}, 400

        user = User.query.filter_by(_uid=user_uid).first()
        if not user:
            return {'message': 'User not found'}, 404

        if user.pfp:
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], user_uid, user.pfp)
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
                user.delete_pfp()  # Call the delete_pfp method to update the database
                return {'message': 'Profile picture deleted successfully'}, 200
            except Exception as e:
                return {'message': f'An error occurred while deleting the profile picture: {str(e)}'}, 500
        else:
            return {'message': 'Profile picture not set.'}, 404

    @token_required()
    def put(self):
        current_user = g.current_user

        if 'pfp' not in request.json:
            return {'message': 'Base64 image data required.'}, 400

        base64_image = request.json['pfp']
        try:
            image_data = base64.b64decode(base64_image)
            filename = secure_filename(f'{current_user.uid}.png')
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.uid)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            file_path = os.path.join(user_dir, filename)
            with open(file_path, 'wb') as img_file:
                img_file.write(image_data)
            current_user.update(pfp=filename)
            return {'message': 'Profile picture updated successfully'}, 200
        except Exception as e:
            return {'message': f'An error occurred while updating the profile picture: {str(e)}'}, 500

api.add_resource(_PFP, '/pfp')
