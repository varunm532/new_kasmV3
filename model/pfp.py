import base64
import os
from werkzeug.utils import secure_filename
from __init__ import app

def file_upload(file, user_uid):
    filename = secure_filename(file.filename)
    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_uid)
    try:
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        file_path = os.path.join(user_dir, filename)
        file.save(file_path)
        return True 
    except Exception as e:
        print (f'An error occurred while updating the profile picture: {str(e)}')
        return False
    
    
def base64_upload(base64_image, user_uid):
    try:
        image_data = base64.b64decode(base64_image)
        filename = secure_filename(f'{user_uid}.png')
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_uid)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        file_path = os.path.join(user_dir, filename)
        with open(file_path, 'wb') as img_file:
            img_file.write(image_data)
        return True 
    except Exception as e:
        print (f'An error occurred while updating the profile picture: {str(e)}')
        return False