from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #creates and instance of SQLAlchemy

class Graph(db.Model):
    __tablename__ = "graphs" #sets the tablename
    id = db.Column(db.Integer, primary_key=True) #sets the id column to integer and sets it to primary key
    name = db.Column(db.String(100), nullable=False) #creates the name column
    description = db.Column(db.String(250)) #creates the description column
    is_temporary = db.Column(db.Boolean, default=True)  # True if the graph is temporary
    data_points = db.relationship("DataPoint", backref="graph", lazy=True) #defines that the graph has a relationship to datapoints

class DataPoint(db.Model):
    __tablename__ = "data_points"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

    graph_id = db.Column(db.Integer, db.ForeignKey("graphs.id"), nullable=False)

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))