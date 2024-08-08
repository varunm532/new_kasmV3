import requests
from __init__ import app

class KasmUtils:
    @staticmethod
    def get_config():
        SERVER = app.config['KASM_SERVER']
        API_KEY = app.config['KASM_API_KEY']
        API_KEY_SECRET = app.config['KASM_API_KEY_SECRET']
        if not SERVER or not API_KEY or not API_KEY_SECRET:
            return None, {'message': '1 or more keys are required to create a user'}, 400
        return (SERVER, API_KEY, API_KEY_SECRET), None

    @staticmethod
    def authenticate():
        config, error = KasmUtils.get_config()
        if error:
            return error
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            url = SERVER + "/api/public/validate_credentials"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET
            }
            response = requests.post(url, json=data)
            if response.status_code == 401:
                return {'message': 'Invalid credentials'}, 401
        except:
            return {'message': 'Invalid credentials'}, 401

    @staticmethod
    def get_user_id(users, target_username):
        for user in users:
            if user['username'] == target_username:
                print("User found with username: " + target_username)
                print("User ID: " + user['user_id'])
                return user['user_id']
        return None

    @staticmethod
    def get_users(SERVER, API_KEY, API_KEY_SECRET):
        try:
            url = SERVER + "/api/public/get_users"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET
            }
            response = requests.post(url, json=data)
            if response.status_code == 401:
                return {'message': 'Invalid credentials'}, 401

            users = response.json()['users']  # This should be your users list
        except:
            return {'message': 'Invalid credentials'}, 401
        return users

    @staticmethod
    def delete_user(SERVER, API_KEY, API_KEY_SECRET, uid):
        try:
            url = SERVER + "/api/public/delete_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "user_id": uid
                },
                "force": False
            }
            response = requests.post(url, json=data)
            if response.status_code == 401:
                return {'message': 'Invalid credentials'}, 401
        except:
            return {'message': 'Invalid credentials'}, 401
        return response


class KasmCreateUser:
    def post(self, name, uid, password):
        config, error = KasmUtils.get_config()
        if error:
            return error
        SERVER, API_KEY, API_KEY_SECRET = config

        auth_error = KasmUtils.authenticate()
        if auth_error:
            return auth_error

        print("Creating user with name: " + name)

        full_name = name
        words = full_name.split()

        if len(words) > 1:
            first_name = " ".join(words[:-1])  # Join all but the last word for first name
            last_name = words[-1]  # Last word is the last name
        else:
            first_name = words[0]  # Only word is the first name
            last_name = ""  # No last name

        print("First Name:", first_name)
        print("Last Name:", last_name)

        # Check if password doesn't exist
        if password is None:
            return {'message': f'Password is missing'}, 400

        kasm_url = SERVER + "/api/public/create_user"
        kasm_data = {
            "api_key": API_KEY,
            "api_key_secret": API_KEY_SECRET,
            "target_user": {
                "username": uid,
                "first_name": first_name,
                "last_name": last_name,
                "locked": False,
                "disabled": False,
                "organization": "All Users",
                "phone": "123-456-7890",
                "password": password,
            }
        }
        print(kasm_data)
        # send a post request to the kasm server
        response = requests.post(kasm_url, json=kasm_data)
        print(response)


class KasmDeleteUser:
    def post(self, user):
        config, error = KasmUtils.get_config()
        if error:
            return error
        SERVER, API_KEY, API_KEY_SECRET = config

        auth_error = KasmUtils.authenticate()
        if auth_error:
            return auth_error

        user_id = KasmUtils.get_user_id(KasmUtils.get_users(SERVER, API_KEY, API_KEY_SECRET), user)
        if user_id is None:
            return {'message': f'User {user} not found'}, 404

        KasmUtils.delete_user(SERVER, API_KEY, API_KEY_SECRET, user_id)

        print("Deleting user with username: " + user + " and user_id: " + user_id)