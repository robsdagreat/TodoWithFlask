from flask import Flask, render_template
import secrets
from extensions import db, jwt, cache, socketio
from auth import auth
from todos import todos
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'simple'

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(todos, url_prefix='/todos')

    # Set up the index route
    @app.route('/')
    def index():
        try:
            verify_jwt_in_request(optional=True)
            user = get_jwt_identity()
            is_logged_in = user is not None
            
        except:
            is_logged_in=False 
            
        return render_template('index.html', is_logged_in=is_logged_in)       

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
    
    socketio.run(app, debug=True)
