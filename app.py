import os
import requests
import json
import openai
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
import plotly
import plotly.graph_objects as go
from flask_cors import CORS

# Import your models AFTER initializing db
from models import db, Graph, DataPoint
from utils.services.oura_fetch_and_store import fetch_oura_data, flatten_oura_chunks, clean_data, store_oura_data
from ai_analysis import openai_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# CORS configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:5001,http://127.0.0.1:5173,http://127.0.0.1:5001').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})
app.secret_key = 'your-unique-secret-key'

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# OpenAI API setup
openai.api_key = os.getenv("OPENAI_API_KEY")

select_keys = [
    "day",
    "awake_time",
    "average_hrv",
    "average_heart_rate",
    "average_breath",
    "deep_sleep_duration",
    "rem_sleep_duration",
    "total_sleep_duration"
]
keys_in_minutes = [
    "awake_time",
    "deep_sleep_duration",
    "rem_sleep_duration",
    "total_sleep_duration"
]

#SPA preparation: 
@app.route('/api/graphs', methods=['GET'])
def get_graphs(): 
    try:
        all_graphs = Graph.query.filter(or_(Graph.is_temporary==None, Graph.is_temporary==False)).all()

        graph_list = []

        for g in all_graphs: 
            fig_for_graph = create_plot_for_graph(g)
            graph_list.append({
                "title": g.name,
                "figure": fig_for_graph,
                "graph_id": g.id
                })
        return jsonify(graph_list)
    except Exception as e:
        print(f"ERROR in get_graphs: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/graphs/<int:graph_id>', methods=['DELETE'])
def delete_graph_api(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    DataPoint.query.filter_by(graph_id=graph_id).delete()  # Delete related data points
    db.session.delete(graph)
    db.session.commit()
    return jsonify({"message": "Graph deleted", "graph_id": graph_id}), 200

@app.route('/api/graphs', methods=['POST'])
def create_graph_api():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"error": "Graph name is required"}), 400
        
    graph = Graph(name=name, description=description, is_temporary=False)
    db.session.add(graph)
    db.session.commit()
    
    # Return the newly created graph with its ID
    return jsonify({
        "message": "Graph created successfully",
        "graph": {
            "graph_id": graph.id,
            "title": graph.name,
            "description": graph.description
        }
    }), 201

@app.route('/api/ai-analyze/<int:graph_id>', methods=['POST'])
def ai_analysis(graph_id): 
    
    graph = Graph.query.get_or_404(graph_id) #get the graph
    data_points = graph.data_points #get the datapoints in the graph
    data_str_list = [] #create empty list

    for dp in data_points: #iterate over items in the data_points list
        data_str_list.append(f"{dp.date}: {dp.metric_name} = {dp.value}") #input one string for each datapoint into an array
    data_str = " ".join(data_str_list) #join the array of string together

    prompt_text = f"""You are a longevity expert working alongside Peter Attia. Analyze this data and generate useful insights and recommendations. What patterns do you see and what is worth trying out. Here is the data: {data_str}"""
    ai_response = openai_connection(prompt_text)
    return jsonify({"ai_analysis": ai_response})

@app.route('/api/datapoints', methods=['POST'])
def add_data_points():
    data = request.get_json()
    graph_id = data.get('graph_id')
    data_points = data.get('data_points', [])

    if not graph_id or not data_points:
        return jsonify({'error': 'Missing required data'}), 400

    try:
        graph = Graph.query.get(graph_id)
        if not graph:
            return jsonify({'error': 'Graph not found'}), 404

        added_points = []
        for point in data_points:
            date = datetime.strptime(point['date'], '%Y-%m-%d').date()
            new_point = DataPoint(
                graph_id=graph_id,
                date=date,
                metric_name=point['metric_name'],
                value=float(point['value'])
            )
            db.session.add(new_point)
            added_points.append({
                'date': date.isoformat(),
                'metric_name': point['metric_name'],
                'value': float(point['value'])
            })

        db.session.commit()
        return jsonify({
            'message': 'Data points added successfully',
            'data_points': added_points
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#Old routes below: 

@app.route('/', methods=['GET'])
def dashboard(): 
    all_graphs = Graph.query.filter(or_(Graph.is_temporary==None, Graph.is_temporary==False)).all()

    user_figs = []

    for graph_obj in all_graphs: 
        fig_for_graph = create_plot_for_graph(graph_obj)
        user_figs.append({
            'title': graph_obj.name,
            'figure': fig_for_graph, 
            'graph_id': graph_obj.id
        })

    return render_template('index.html', user_figs=user_figs)

@app.route('/new-graph', methods=['GET', 'POST'])
def new_graph(): 
    if request.method == 'POST': 
        name = request.form.get('name')
        description = request.form.get('description')
        if name: 
            graph = Graph(name=name, description=description)
            db.session.add(graph)
            db.session.commit()
            return redirect(url_for('dashboard')) ###This function generates a URL for the view function (or endpoint) named 'dashboard'.
    return render_template('new_graph.html')

def create_plot_for_graph(graph_obj):
    # Check if this graph uses tracked metrics (dynamic) or static data points (legacy)
    if graph_obj.tracked_metrics:
        # Dynamic graph: fetch live data for tracked metrics
        try:
            tracked_metrics_list = json.loads(graph_obj.tracked_metrics)
            metrics_data = {}
            
            for metric in tracked_metrics_list:
                # Get all data points for this metric from any graph
                live_points = DataPoint.query.filter_by(metric_name=metric).all()
                sorted_points = sorted(live_points, key=lambda dp: dp.date)
                
                metrics_data[metric] = []
                for dp in sorted_points:
                    metrics_data[metric].append({
                        "x": dp.date.strftime("%Y-%m-%d"),
                        "y": dp.value
                    })
                    
            final_series = []
            for metric_name, data_points in metrics_data.items():
                final_series.append({
                    "name": metric_name,
                    "data": data_points
                })
            
            return final_series
            
        except (json.JSONDecodeError, AttributeError):
            # Fall back to static data if JSON parsing fails
            pass
    
    # Legacy graph: use static data points
    points = sorted(graph_obj.data_points, key=lambda dp: (dp.metric_name, dp.date))
    if not points:
        return [{
            "name": "Empty",
            "data": []
        }]
        
    metrics_data = {}
    for dp in points:
        metric = dp.metric_name
        if metric not in metrics_data:
            metrics_data[metric] = []
        metrics_data[metric].append({
            "x": dp.date.strftime("%Y-%m-%d"),
            "y": dp.value
        })
    
    final_series = []
    for metric_name, data_points in metrics_data.items():
        final_series.append({
            "name": metric_name,
            "data": data_points
        })

    return final_series

@app.route('/oura_connect', methods=['GET', 'POST'])
def connect_oura(): 
    if request.method == 'POST':
        token = request.form.get('token')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not token or not start_date or not end_date: 
            return redirect(url_for('connect-oura'))
        
        all_data = fetch_oura_data(token, start_date, end_date)
        flattened = flatten_oura_chunks(all_data)
        cleaned = clean_data(flattened)
        store_oura_data(cleaned)

        return redirect(url_for('dashboard'))
    
    return render_template('oura_connect.html')

@app.route('/add-data', methods=['GET', 'POST'])
def add_data(): 
    if request.method == 'POST': 
        dates = request.form.getlist('date[]')
        metric_names = request.form.getlist('metric_name[]')
        values = request.form.getlist('value[]')
        graph_id = request.form.get('graph_id')

        new_data_points = []

        for d_str, m_name, val_str in zip(dates, metric_names, values): 
            date_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
            val = float(val_str)

            dp = DataPoint (
                date=date_obj, 
                metric_name=m_name, 
                value=val, 
                graph_id=int(graph_id)
            )
            new_data_points.append(dp)
        
        db.session.bulk_save_objects(new_data_points)
        db.session.commit()

        return redirect(url_for('dashboard'))
    
    graphs = Graph.query.all()
    return render_template('add_data.html', graphs=graphs)
    
@app.route('/graph/<int:graph_id>', methods=['GET', 'POST'])
def show_graph_table(graph_id): 
    graph_obj = Graph.query.get_or_404(graph_id)
    
    print(f"graph found {graph_obj.name}")

    if request.method == "POST":
        print("POST form data:", request.form)
        new_name = request.form.get(f"graph_name_{graph_id}")
        print(f"Received graph name: {new_name}")  # Debugging
        if new_name: 
            graph_obj.name = new_name
        
        # Process form submission (editing data points)
        data_point_ids = request.form.getlist("data_point_id")

        for dp_id in data_point_ids:
            # Extract data from the form
            date_str = request.form.get(f"date_{dp_id}")
            metric_name = request.form.get(f"metric_name_{dp_id}")
            value_str = request.form.get(f"value_{dp_id}")

            # Convert date string to a date object
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Fetch the actual DataPoint from DB
            dp_obj = DataPoint.query.get(dp_id)
            if dp_obj:
                # Update the fields
                dp_obj.date = date_obj
                dp_obj.metric_name = metric_name
                dp_obj.value = float(value_str)
        
        # Save changes to the database
        db.session.commit()
        return redirect(url_for('show_graph_table', graph_id=graph_id))

    data_points = graph_obj.data_points
    return render_template("graph_table.html", graph=graph_obj, data_points=data_points)

@app.route('/ai-analyze/<int:graph_id>', methods=['POST'])
def ai_analysis_legacy(graph_id): 
    
    graph = Graph.query.get_or_404(graph_id) #get the graph
    data_points = graph.data_points #get the datapoints in the graph
    data_str_list = [] #create empty list

    for dp in data_points: #iterate over items in the data_points list
        data_str_list.append(f"{dp.date}: {dp.metric_name} = {dp.value}") #input one string for each datapoint into an array
    data_str = " ".join(data_str_list) #join the array of string together

    prompt_text = f"""You are a longevity expert working alongside Peter Attia. Analyze this data and generate useful insights and recommendations. What patterns do you see and what is worth trying out. Here is the data: {data_str}"""
    ai_response = openai_connection(prompt_text)
    return jsonify({"ai_analysis": ai_response})

@app.route('/delete_graph/<int:graph_id>', methods=['POST'])
def delete_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    DataPoint.query.filter_by(graph_id=graph_id).delete()  # Delete related data points
    db.session.delete(graph)  # Delete graph
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_datapoint/<int:data_point_id>', methods=['POST'])
def delete_datapoint(data_point_id):
    data_point = DataPoint.query.get_or_404(data_point_id)
    graph_id = data_point.graph_id  # remember which graph this row belongs to
    db.session.delete(data_point)
    db.session.commit()
    return redirect(url_for('show_graph_table', graph_id=graph_id))

@app.route('/integrations', methods=['GET'])
def integrations(): 
    return render_template('integrations.html')

@app.route('/explorer', methods=['GET'])
def explorer(): 
    temp_graph_id = session.get('temp_graph_id')
    if temp_graph_id: 
        temp_graph = Graph.query.filter_by(id=temp_graph_id, is_temporary=True).first()
    else: 
        temp_graph = None

    if not temp_graph: 
        temp_graph = Graph(
            name = "Temporary explorer graph", 
            description = "Graph for exploration",
            is_temporary = True
        )
        db.session.add(temp_graph)
        db.session.commit()
        session['temp_graph_id'] = temp_graph.id

    metric_tuples = db.session.query(DataPoint.metric_name).distinct().all()
    metrics = [m[0] for m in metric_tuples]
    metrics.sort()

    plot_data = create_plot_for_graph(temp_graph)
    
    return render_template('explorer.html', metrics=metrics, graph_id=temp_graph.id, plot_data=plot_data, graph_name=temp_graph.name)

@app.route('/add-temp-graph', methods=['POST'])
def add_temp_graph():
    data = request.get_json()
    metrics_list = data.get('metrics', [])

    temp_graph_id = session.get('temp_graph_id')
    if not temp_graph_id: 
        return redirect(url_for('explorer'))
    
    temp_graph = Graph.query.filter_by(id=temp_graph_id, is_temporary=True).first()
    if not temp_graph:
        return redirect(url_for('explorer'))
    
    # Store tracked metrics instead of copying data points
    temp_graph.tracked_metrics = json.dumps(metrics_list)
    temp_graph.is_temporary = False
    db.session.commit()    
    session.pop('temp_graph_id', None)

    return jsonify({'status': 'ok'})

@app.route('/oura_connect', methods=['GET'])
def oura_connect(): 
    return render_template('oura_connect.html')

# Explorer API Routes
@app.route('/api/explorer/init', methods=['POST'])
def api_init_explorer():
    # Create a new temporary graph
    temp_graph = Graph(
        name="Temporary explorer graph",
        description="Graph for exploration",
        is_temporary=True
    )
    db.session.add(temp_graph)
    db.session.commit()

    # Get all unique metric names
    metric_tuples = db.session.query(DataPoint.metric_name).distinct().all()
    metrics = sorted([m[0] for m in metric_tuples])

    return jsonify({
        'graph_id': temp_graph.id,
        'available_metrics': metrics
    })

@app.route('/api/metric-data/<string:metric>', methods=['GET'])
def api_get_metric_data(metric):
    data_points = DataPoint.query.filter_by(metric_name=metric).all()
    sorted_points = sorted(data_points, key=lambda dp: dp.date)

    series_data = [{
        "x": dp.date.strftime("%Y-%m-%d"),
        "y": dp.value
    } for dp in sorted_points]

    return jsonify({
        "series": {
            "name": metric,
            "data": series_data
        }
    })

@app.route('/api/explorer/save', methods=['POST'])
def api_save_explorer():
    data = request.get_json()
    metrics_list = data.get('metrics', [])

    if not metrics_list:
        return jsonify({'error': 'No metrics selected'}), 400

    # Create a new permanent graph with tracked metrics
    new_graph = Graph(
        name=f"Explorer Graph ({', '.join(metrics_list)})",
        description=f"Graph created from explorer with metrics: {', '.join(metrics_list)}",
        is_temporary=False,
        tracked_metrics=json.dumps(metrics_list)  # Store metrics as JSON
    )
    db.session.add(new_graph)
    db.session.commit()
    
    return jsonify({'status': 'success', 'graph_id': new_graph.id})

@app.route('/api/explorer/cancel', methods=['POST'])
def api_cancel_explorer():
    return jsonify({'status': 'success'})

@app.route('/api/oura-connect', methods=['POST'])
def api_connect_oura():
    data = request.get_json()
    token = data.get('token')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not token or not start_date or not end_date:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        all_data = fetch_oura_data(token, start_date, end_date)
        flattened = flatten_oura_chunks(all_data)
        cleaned = clean_data(flattened)
        rows_inserted = store_oura_data(cleaned)
        
        if rows_inserted > 0:
            return jsonify({'message': f'Oura data synced successfully! Added {rows_inserted} new data points.'}), 200
        else:
            return jsonify({'message': 'Sync completed, but no new data was found. All data may already be up to date.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graphs/<int:graph_id>', methods=['GET'])
def get_graph_details(graph_id):
    try:
        graph = Graph.query.get_or_404(graph_id)
        data_points = [{
            'id': dp.id,
            'date': dp.date.strftime('%Y-%m-%d'),
            'metric_name': dp.metric_name,
            'value': dp.value
        } for dp in sorted(graph.data_points, key=lambda x: (x.metric_name, x.date))]
        
        return jsonify({
            'id': graph.id,
            'name': graph.name,
            'description': graph.description,
            'data_points': data_points
        })
    except Exception as e:
        print(f"Error in get_graph_details: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/graphs/<int:graph_id>', methods=['PUT'])
def update_graph_details(graph_id):
    try:
        data = request.get_json()
        graph = Graph.query.get_or_404(graph_id)
        
        # Update graph name if provided
        if 'name' in data:
            graph.name = data['name']
            
        # Update data points if provided
        if 'data_points' in data:
            for point_data in data['data_points']:
                point = DataPoint.query.get(point_data['id'])
                if point and point.graph_id == graph_id:  # Ensure point belongs to this graph
                    point.date = datetime.strptime(point_data['date'], '%Y-%m-%d').date()
                    point.metric_name = point_data['metric_name']
                    point.value = float(point_data['value'])
        
        db.session.commit()
        return jsonify({'message': 'Graph updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_graph_details: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Add utility function to convert existing graphs to tracked metrics
def convert_static_graph_to_tracked(graph_id):
    """Convert a static graph to use tracked metrics"""
    try:
        graph = Graph.query.get(graph_id)
        if not graph or graph.tracked_metrics:
            return False  # Already converted or doesn't exist
        
        # Get unique metrics from this graph's data points
        existing_metrics = db.session.query(DataPoint.metric_name).filter_by(graph_id=graph_id).distinct().all()
        metrics_list = [m[0] for m in existing_metrics]
        
        if not metrics_list:
            return False  # No metrics to track
        
        # Store tracked metrics and clear static data points
        graph.tracked_metrics = json.dumps(metrics_list)
        DataPoint.query.filter_by(graph_id=graph_id).delete()
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error converting graph {graph_id}: {str(e)}")
        return False

@app.route('/api/graphs/<int:graph_id>/convert-to-dynamic', methods=['POST'])
def convert_graph_to_dynamic(graph_id):
    """API endpoint to convert a static graph to dynamic tracked metrics"""
    try:
        success = convert_static_graph_to_tracked(graph_id)
        if success:
            return jsonify({'message': f'Graph {graph_id} converted to dynamic tracking successfully'})
        else:
            return jsonify({'error': 'Failed to convert graph or graph already dynamic'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/convert-all-graphs', methods=['POST'])
def convert_all_graphs_to_dynamic():
    """Convert all existing static graphs to dynamic tracked metrics"""
    try:
        static_graphs = Graph.query.filter(
            Graph.tracked_metrics.is_(None),
            Graph.is_temporary != True
        ).all()
        
        converted_count = 0
        for graph in static_graphs:
            if convert_static_graph_to_tracked(graph.id):
                converted_count += 1
        
        return jsonify({
            'message': f'Successfully converted {converted_count} graphs to dynamic tracking',
            'converted_count': converted_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

""" ###for testing: 
response = requests.get(url, headers=headers, params=params)
data = response.json()
cleaned_data = clean_data(data)
df = pd.DataFrame(cleaned_data)
df['day'] = pd.to_datetime(df['day'])
graphJSON = plot_sleep_metrics(df,select_keys)
 """

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(debug=True, port=port)

