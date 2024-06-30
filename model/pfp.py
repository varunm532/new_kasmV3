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
