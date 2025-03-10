import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    
    # Don't load config from config.py if it's already been loaded
    if not app.config.get('TESTING'):
        app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.contacts import contacts_bp
    from app.routes.groups import groups_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts')
    app.register_blueprint(groups_bp, url_prefix='/api/groups')
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from app.models.user import User
        from app.models.contact import Contact
        from app.models.group import Group
        
        return {
            'db': db, 
            'User': User,
            'Contact': Contact,
            'Group': Group
        }
    
    return app 