# imports from flask
from flask import redirect, render_template, request, url_for, jsonify  # import render_template from "public" flask libraries
from flask_login import current_user, login_user, logout_user
from flask.cli import AppGroup
import jwt 
from flask_login import current_user, login_required
from flask import current_app

# import "objects" from "this" project
from __init__ import app, db, login_manager  # Key Flask objects 

# API endpoints
from api.covid import covid_api 
from api.joke import joke_api 
from api.user import user_api 
from api.player import player_api
from api.titanic import titanic_api
# database Initialization functions
from model.users import User, initUsers, Section 
from model.players import initPlayers
from model.titanicML import initTitanic
# server only Views
from views.algorithm.algorithm import algorithm_views 
from views.recipes.recipe import recipe_views 
from views.projects.projects import project_views

# register URIs for api endpoints
app.register_blueprint(joke_api) 
app.register_blueprint(covid_api) 
app.register_blueprint(user_api) 
app.register_blueprint(player_api)
app.register_blueprint(titanic_api)
# register URIs for server pages
app.register_blueprint(algorithm_views) 
app.register_blueprint(recipe_views) 
app.register_blueprint(project_views) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/')  # connects default URL to index() function
def index():
    print("Home:", current_user)
    return render_template("index.html")

@app.route('/table/')  # connects /table/ URL
def table():
    return render_template("table.html")

@app.route('/login/')  # connects /table/ URL
def login_page():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    # authenticate user
    user = User.query.filter_by(_uid=request.form['username']).first()
    if user and user.is_password(request.form['password']):
        login_user(user)
        
        # Generate JWT token
        token = jwt.encode(
            {"_uid": user._uid},
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        
        # Create a response and set the token as a cookie
        resp = redirect(url_for('index'))
        resp.set_cookie(current_app.config["JWT_TOKEN_NAME"], 
                        token,
                        max_age=3600,
                        secure=True,
                        httponly=True,
                        path='/',
                        samesite='None')
        
        print("Logged in:", current_user)
        print("Token:", token)
        
        return resp
    else:
        return 'Invalid username or password'

    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/users/table')
@login_required
def utable():
    users = User.query.all()

    user_data = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": user.name,
            "uid": user.uid,
            "role": user.role,
            "kasm_server_needed": user.kasm_server_needed,
            "status": user.status,
            "classes": user.sections
        }

    return render_template("utable.html", user_data=user_data, current_user=current_user)

@app.route('/users/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    user.kasm_server_needed = data.get('kasmServerNeeded', user.kasm_server_needed)
    user.status = data.get('status', user.status)

    db.session.commit()

    return jsonify({
        'kasmServerNeeded': user.kasm_server_needed,
        'status': user.status,
    })


@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404



# Create an AppGroup for custom commands
custom_cli = AppGroup('custom', help='Custom commands')

# Define a command to run the data generation functions
@custom_cli.command('generate_data')
def generate_data():
    initUsers()

# Register the custom command group with the Flask application
app.cli.add_command(custom_cli)
        
# this runs the flask application on the development server
if __name__ == "__main__":
    # change name for testing
    app.run(debug=True, host="0.0.0.0", port="8086")
