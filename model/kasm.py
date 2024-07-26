from flask_restful import Resource # used for REST API building
import os
from dotenv import load_dotenv
import requests
from api.jwt_authorize import token_required
from model.user import User


class CreateUser(Resource):
    def post(self, name, uid, password):
        # Checking if system has the required environment variables
        if not os.getenv('KASM_API_KEY_SECRET') or not os.getenv('KASM_API_KEY'):
            #gracefully prevent kasm.py from continueing if the environment variables are not set
            return {'message': 'KASM_API_KEY_SECRET or KASM_API_KEY not set'}, 400
        else:
            #checking if credentials are valid
            try:
                url = os.getenv('KASM_SERVER') + "/api/public/get_users"
                data={
                    "api_key": os.getenv('KASM_API_KEY'),
                    "api_key_secret": os.getenv('KASM_API_KEY_SECRET')
                }
                response = requests.post(url, json=data)
                if response.status_code == 401:
                    return {'message': 'Invalid credentials'}, 401
            except:
                return {'message': 'Invalid credentials'}, 401

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

            #Check if password doesnt exist
            if password is None:
                return {'message': f'Password is missing'}, 400

            kasm_url = os.getenv('KASM_SERVER') + "/api/public/create_user"
            kasm_data = {
                "api_key": os.getenv('KASM_API_KEY'),
                "api_key_secret": os.getenv('KASM_API_KEY_SECRET'),
                "target_user": {
                    "username" : uid,
                    "first_name" : first_name,
                    "last_name" : last_name,
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