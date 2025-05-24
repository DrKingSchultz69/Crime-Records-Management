from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://root:password@localhost/TNcrimeTrack')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import and register blueprints
from routes.auth import auth_bp
from routes.crime_records import crime_records_bp
from routes.complaints import complaints_bp
from routes.investigations import investigations_bp
from routes.reports import reports_bp
from routes.locations import locations_bp
from routes.police_stations import police_stations_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(crime_records_bp, url_prefix='/api/crime-records')
app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
app.register_blueprint(investigations_bp, url_prefix='/api/investigations')
app.register_blueprint(reports_bp, url_prefix='/api/reports')
app.register_blueprint(locations_bp, url_prefix='/api/locations')
app.register_blueprint(police_stations_bp, url_prefix='/api/police-stations')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
