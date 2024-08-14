from flask import Flask
from flask_jwt_extended import JWTManager
from auth import auth
from todos import todos
import secrets

app = Flask(__name__)

def generate_unique_key(length=32):
    return secrets.token_urlsafe(length)

app.config['JWT_SECRET_KEY'] = generate_unique_key()
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(todos, url_prefix='/todos')

if __name__ == '__main__':
    app.run(debug=True)