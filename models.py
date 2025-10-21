from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #creates and instance of SQLAlchemy

class Graph(db.Model):
    __tablename__ = "graphs" #sets the tablename
    id = db.Column(db.Integer, primary_key=True) #sets the id column to integer and sets it to primary key
    name = db.Column(db.String(100), nullable=False) #creates the name column
    description = db.Column(db.String(250)) #creates the description column
    is_temporary = db.Column(db.Boolean, default=True)  # True if the graph is temporary
    tracked_metrics = db.Column(db.Text)  # JSON string of metrics this graph should display
    data_points = db.relationship("DataPoint", backref="graph", lazy=True) #defines that the graph has a relationship to datapoints

class DataPoint(db.Model):
    __tablename__ = "data_points"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

    graph_id = db.Column(db.Integer, db.ForeignKey("graphs.id"), nullable=True)

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Oura integration fields
    oura_api_token = db.Column(db.String(500))  # Encrypted Oura API token
    last_oura_sync = db.Column(db.DateTime)  # Last sync timestamp
    
    # Fitbit integration fields
    fitbit_access_token = db.Column(db.String(500))  # Fitbit OAuth access token
    fitbit_refresh_token = db.Column(db.String(500))  # Fitbit OAuth refresh token
    fitbit_token_expires_at = db.Column(db.DateTime)  # Token expiration time
    fitbit_user_id = db.Column(db.String(100))  # Fitbit user ID
    last_fitbit_sync = db.Column(db.DateTime)  # Last Fitbit sync timestamp
    
    # General sync settings
    sync_frequency = db.Column(db.String(20), default='manual')  # 'manual', 'daily', 'weekly'
    sync_enabled = db.Column(db.Boolean, default=False)  # Enable/disable automatic sync
    last_automatic_sync = db.Column(db.DateTime)  # Last automatic sync timestamp
    next_scheduled_sync = db.Column(db.DateTime)  # Next scheduled sync timestamp
    selected_dashboard_metrics = db.Column(db.Text)  # JSON string of selected metrics for dashboard
    sync_logs = db.relationship("SyncLog", backref="user", lazy=True)

class SyncLog(db.Model):
    __tablename__ = "sync_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    sync_type = db.Column(db.String(20), nullable=False)  # 'manual', 'scheduled'
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed', 'in_progress'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    records_imported = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    completed_at = db.Column(db.DateTime)

class Experiment(db.Model):
    __tablename__ = "experiments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    period = db.Column(db.String(50), nullable=False)  # '1-week', '2-weeks', 'custom'
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    driver = db.Column(db.String(200))
    metric_of_interest = db.Column(db.String(100), nullable=False)
    benchmark = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50))
    icon_color = db.Column(db.String(7))  # Hex color code
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())