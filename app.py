import os
import json
import openai
from datetime import datetime, date, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from flask_cors import CORS
from flask_apscheduler import APScheduler

# Import your models AFTER initializing db
from models import db, Graph, DataPoint, Experiment, User, SyncLog
from utils.services.oura_fetch_and_store import fetch_oura_data, flatten_oura_chunks, clean_data, store_oura_data
from utils.services.oura_sync_manager import OuraSyncManager
from ai_analysis import openai_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# CORS configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Use environment variable for secret key
app.secret_key = os.getenv('SECRET_KEY', 'your-unique-secret-key-change-in-production')

database_url = os.getenv("DATABASE_URL")
print(f"Using DATABASE_URL: {database_url}")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# Flask-APScheduler configuration
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'UTC'

# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Initialize Oura sync manager
oura_sync_manager = OuraSyncManager(scheduler)

# OpenAI API setup
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/api/upload/process-notes', methods=['POST'])
def process_notes():
    try:
        data = request.json
        notes = data.get('notes', '')
        clarifications = data.get('clarifications', '')
        
        if not notes:
            return jsonify({"error": "No notes provided"}), 400
        
        # Determine if we need to chunk the data
        notes_length = len(notes)
        chunk_threshold = 3000  # characters per chunk
        max_chunk_size = 2000   # characters per chunk for AI processing
        
        if notes_length > chunk_threshold:
            # Split into chunks and process sequentially
            return process_large_dataset(notes, clarifications, max_chunk_size)
        else:
            # Process normally for smaller datasets
            return process_single_chunk(notes, clarifications)
            
    except Exception as e:
        print(f"Error processing notes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to process notes"}), 500

def process_large_dataset(notes, clarifications, max_chunk_size):
    """Process large datasets by chunking them and processing sequentially"""
    try:
        # Split notes into chunks
        chunks = split_notes_into_chunks(notes, max_chunk_size)
        total_chunks = len(chunks)
        
        print(f"Processing {total_chunks} chunks for large dataset")
        
        all_structured_data = []
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{total_chunks}")
            
            # Process each chunk
            chunk_result, status_code = process_single_chunk(chunk, clarifications)
            
            if status_code == 200:
                chunk_data = chunk_result
                if chunk_data.get('success') and 'structured_data' in chunk_data:
                    all_structured_data.extend(chunk_data['structured_data'])
                elif chunk_data.get('needs_clarification'):
                    # If any chunk needs clarification, return that
                    return jsonify(chunk_data), status_code
            else:
                # If any chunk fails, return the error
                return jsonify(chunk_result), status_code
        
        # Combine all results
        return jsonify({
            "success": True,
            "structured_data": all_structured_data,
            "count": len(all_structured_data),
            "chunks_processed": total_chunks
        })
        
    except Exception as e:
        print(f"Error in large dataset processing: {str(e)}")
        return jsonify({"error": f"Failed to process large dataset: {str(e)}"}), 500

def split_notes_into_chunks(notes, max_chunk_size):
    """Split notes into logical chunks based on workout sessions"""
    lines = notes.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line)
        
        # If adding this line would exceed the chunk size, start a new chunk
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def process_single_chunk(notes, clarifications):
    """Process a single chunk of notes"""
    try:
        # Step 1: Check if data needs clarification (only for first chunk or if no clarifications provided)
        if not clarifications:
            clarification_prompt = f"""
            Analyze these workout notes and determine if they need clarification before structuring.
            
            Notes:
            {notes}
            
            If the data is clear and can be structured directly, respond with just "clear".
            If clarification is needed, ask specific questions about unclear elements.
            
            Examples of unclear elements:
            - Unclear abbreviations (e.g., "BP" could mean "Bench Press" or "Back Pain")
            - Missing units (e.g., "70" without specifying kg/lbs)
            - Ambiguous dates or times
            - Unclear exercise names
            
            Respond with "clear" if the data is unambiguous, or ask specific questions if clarification is needed.
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "developer",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "You are a data clarification assistant. Determine if raw notes need clarification or can be structured directly."
                                }
                            ]
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": clarification_prompt
                                }
                            ]
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.1
                )
                ai_response = response.choices[0].message.content.strip()
            except openai.RateLimitError as e:
                return {"error": "OpenAI rate limit exceeded. Please wait a moment and try again."}, 429
            except Exception as e:
                return {"error": f"OpenAI API error: {str(e)}"}, 500
            
            # Check if the response is "clear" or contains questions
            if ai_response.lower() == "clear":
                # Data is clear, proceed directly to structuring
                clarifications = ""  # No clarifications needed
            else:
                # Parse questions from the response
                questions = [q.strip() for q in ai_response.split('\n') if q.strip()]
                return {
                    "needs_clarification": True,
                    "questions": questions
                }, 200
        
        # Step 2: Use clarifications to structure the data (or structure directly if clear)
        structuring_prompt = f"""
        Use the provided clarifications to structure the raw notes into organized data points.
        
        Raw Notes:
        {notes}
        
        Clarifications:
        {clarifications}
        
        Please structure this into a JSON array where each object has:
        - metric_name: the name of the metric (e.g., "Rowing Distance", "Workout Duration")
        - value: the numeric value
        - date: the date in YYYY-MM-DD format
        - unit: the unit of measurement (e.g., "meters", "minutes", "sets")
        
        Use the clarifications to understand what each number and abbreviation means.
        If there are multiple values for the same metric, create separate entries.
        
        Return only the JSON array, no additional text.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are a data extraction assistant. Extract structured data from raw notes and return only valid JSON."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": structuring_prompt
                            }
                        ]
                    }
                ],
                max_tokens=4000,  # Reduced token limit for chunks
                temperature=0.1
            )
            
            # Extract the JSON response
            ai_response = response.choices[0].message.content.strip()
            print(f"AI Response: {ai_response}")
        except openai.RateLimitError as e:
            return {"error": "OpenAI rate limit exceeded. Please wait a moment and try again."}, 429
        except Exception as e:
            return {"error": f"OpenAI API error: {str(e)}"}, 500
        
        # Clean up the response - remove markdown code blocks if present
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]  # Remove ```json
        if ai_response.startswith('```'):
            ai_response = ai_response[3:]  # Remove ```
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]  # Remove trailing ```
        
        ai_response = ai_response.strip()
        
        # Try to parse the JSON response
        try:
            structured_data = json.loads(ai_response)
            
            # Validate the structure
            if not isinstance(structured_data, list):
                return {"error": "AI response is not a valid array"}, 500
            
            # Process each data point
            processed_data = []
            for item in structured_data:
                if isinstance(item, dict) and 'metric_name' in item and 'value' in item:
                    processed_data.append({
                        'metric_name': item.get('metric_name', ''),
                        'value': float(item.get('value', 0)),
                        'date': item.get('date', datetime.now().strftime('%Y-%m-%d')),
                        'unit': item.get('unit', '')
                    })
            
            return {
                "success": True,
                "structured_data": processed_data,
                "count": len(processed_data)
            }, 200
            
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON"}, 500
            
    except Exception as e:
        print(f"Error processing single chunk: {str(e)}")
        return {"error": f"Failed to process chunk: {str(e)}"}, 500

# Save structured data from uploads
@app.route('/api/upload/save-data', methods=['POST'])
def save_upload_data():
    try:
        data = request.json
        structured_data = data.get('structured_data', [])
        
        if not structured_data:
            return jsonify({"error": "No structured data provided"}), 400
        
        added_points = []
        for point in structured_data:
            date = datetime.strptime(point['date'], '%Y-%m-%d').date()
            new_point = DataPoint(
                date=date,
                metric_name=point['metric_name'],
                value=float(point['value'])
            )
            db.session.add(new_point)
            added_points.append({
                'date': date.isoformat(),
                'metric_name': point['metric_name'],
                'value': float(point['value']),
                'unit': point.get('unit', '')
            })
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Successfully saved {len(added_points)} data points',
            'data_points': added_points
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving upload data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to save data"}), 500

# API Routes
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
    tracked_metrics = data.get('tracked_metrics', [])
    
    if not name:
        return jsonify({"error": "Graph name is required"}), 400
        
    graph = Graph(
        name=name, 
        description=description, 
        is_temporary=False,
        tracked_metrics=json.dumps(tracked_metrics) if tracked_metrics else None
    )
    db.session.add(graph)
    db.session.commit()
    
    # Return the newly created graph with its ID
    return jsonify({
        "message": "Graph created successfully",
        "graph": {
            "graph_id": graph.id,
            "title": graph.name,
            "description": graph.description,
            "tracked_metrics": tracked_metrics
        }
    }), 201

@app.route('/api/ai-analyze/<int:graph_id>', methods=['POST'])
def ai_analysis(graph_id): 
    graph = Graph.query.get_or_404(graph_id)
    data_points = graph.data_points
    data_str_list = []

    for dp in data_points:
        data_str_list.append(f"{dp.date}: {dp.metric_name} = {dp.value}")
    data_str = " ".join(data_str_list)

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

@app.route('/api/metrics', methods=['GET'])
def get_available_metrics():
    """Get all available metrics without creating a temporary graph"""
    try:
        # Get all unique metrics from the database
        metrics = db.session.query(DataPoint.metric_name).distinct().all()
        metrics = [metric[0] for metric in metrics]
        metrics.sort()
        
        return jsonify({
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    
    # Get all unique metrics from the database
    metrics = db.session.query(DataPoint.metric_name).distinct().all()
    metrics = [metric[0] for metric in metrics]
    metrics.sort()
    
    return jsonify({
        'temp_graph_id': temp_graph.id,
        'metrics': metrics
    })

@app.route('/api/metric-data/<string:metric>', methods=['GET'])
def api_get_metric_data(metric):
    # Get all data points for a specific metric
    data_points = DataPoint.query.filter_by(metric_name=metric).order_by(DataPoint.date).all()
    
    plot_data = []
    for dp in data_points:
        plot_data.append({
            'x': dp.date.strftime("%Y-%m-%d"),
            'y': dp.value
        })
    
    return jsonify({
        'metric': metric,
        'data': plot_data
    })

@app.route('/api/explorer/save', methods=['POST'])
def api_save_explorer():
    data = request.get_json()
    temp_graph_id = data.get('temp_graph_id')
    metrics_list = data.get('metrics', [])
    
    temp_graph = Graph.query.filter_by(id=temp_graph_id, is_temporary=True).first()
    if not temp_graph:
        return jsonify({'error': 'Temporary graph not found'}), 404
    
    # Store tracked metrics instead of copying data points
    temp_graph.tracked_metrics = json.dumps(metrics_list)
    temp_graph.is_temporary = False
    db.session.commit()
    
    return jsonify({
        'message': 'Graph saved successfully',
        'graph_id': temp_graph.id
    })

@app.route('/api/explorer/cancel', methods=['POST'])
def api_cancel_explorer():
    data = request.get_json()
    temp_graph_id = data.get('temp_graph_id')
    
    temp_graph = Graph.query.filter_by(id=temp_graph_id, is_temporary=True).first()
    if temp_graph:
        db.session.delete(temp_graph)
        db.session.commit()
    
    return jsonify({'message': 'Exploration cancelled'})

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
        store_oura_data(cleaned)
        
        return jsonify({'message': 'Oura data imported successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/save-token', methods=['POST'])
def save_oura_token():
    """Save Oura API token for the current user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        token = data.get('token')
        remember_token = data.get('remember_token', False)
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Ensure token is a string and handle any encoding issues
        if isinstance(token, str):
            # Clean the token - remove any problematic characters
            token = token.strip()
        else:
            return jsonify({'error': 'Token must be a string'}), 400
        
        # For now, we'll use a simple approach - store for a default user
        # In a real app, you'd get the current user from authentication
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            user = User(email='default@neuroflow.app')
            db.session.add(user)
        
        if remember_token:
            user.oura_api_token = token  # In production, encrypt this
        else:
            user.oura_api_token = None
            
        db.session.commit()
        
        return jsonify({
            'message': 'Token saved successfully' if remember_token else 'Token not saved',
            'token_saved': remember_token
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error saving Oura token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/status', methods=['GET'])
def get_oura_status():
    """Get Oura sync status and last sync information"""
    try:
        # For now, we'll use a simple approach - get default user
        user = User.query.filter_by(email='default@neuroflow.app').first()
        
        if not user:
            return jsonify({
                'has_token': False,
                'last_sync': None,
                'sync_frequency': 'manual',
                'recent_syncs': []
            })
        
        # Get recent sync logs (last 10)
        recent_syncs = SyncLog.query.filter_by(user_id=user.id).order_by(SyncLog.started_at.desc()).limit(10).all()
        
        sync_history = []
        for sync in recent_syncs:
            sync_history.append({
                'id': sync.id,
                'sync_type': sync.sync_type,
                'status': sync.status,
                'start_date': sync.start_date.strftime('%Y-%m-%d') if sync.start_date else None,
                'end_date': sync.end_date.strftime('%Y-%m-%d') if sync.end_date else None,
                'records_imported': sync.records_imported,
                'error_message': sync.error_message,
                'started_at': sync.started_at.isoformat() if sync.started_at else None,
                'completed_at': sync.completed_at.isoformat() if sync.completed_at else None
            })
        
        return jsonify({
            'has_token': bool(user.oura_api_token),
            'token': '********************************' if user.oura_api_token else None,
            'last_sync': user.last_oura_sync.isoformat() if user.last_oura_sync else None,
            'sync_frequency': user.sync_frequency or 'manual',
            'recent_syncs': sync_history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/sync-now', methods=['POST'])
def sync_oura_now():
    """Manually trigger Oura sync"""
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    token = data.get('token')  # Allow token to be passed from frontend
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start date and end date are required'}), 400
    
    try:
        # Get user and determine which token to use
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            return jsonify({'error': 'User not found'}), 400
        
        # Use provided token or fall back to stored token
        api_token = token if token and token != '********************************' else user.oura_api_token
        
        if not api_token or api_token == '********************************':
            return jsonify({'error': 'No Oura token found. Please save your token first.'}), 400
        
        # Create sync log entry
        sync_log = SyncLog(
            user_id=user.id,
            sync_type='manual',
            status='in_progress',
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            started_at=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.commit()
        
        try:
            # Fetch and store data
            all_data = fetch_oura_data(api_token, start_date, end_date)
            flattened = flatten_oura_chunks(all_data)
            cleaned = clean_data(flattened)
            store_oura_data(cleaned)
            
            # Count records imported (approximate)
            records_imported = len(cleaned) if cleaned else 0
            
            # Update sync log with success
            sync_log.status = 'success'
            sync_log.records_imported = records_imported
            sync_log.completed_at = datetime.utcnow()
            
            # Update last sync timestamp
            user.last_oura_sync = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Oura data synced successfully',
                'last_sync': user.last_oura_sync.isoformat(),
                'records_imported': records_imported,
                'sync_log_id': sync_log.id
            })
            
        except Exception as sync_error:
            # Update sync log with failure
            sync_log.status = 'failed'
            sync_log.error_message = str(sync_error)
            sync_log.completed_at = datetime.utcnow()
            db.session.commit()
            raise sync_error
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/settings', methods=['PUT'])
def update_oura_settings():
    """Update Oura sync settings"""
    data = request.get_json()
    sync_frequency = data.get('sync_frequency')
    
    if sync_frequency not in ['manual', 'daily', 'weekly']:
        return jsonify({'error': 'Invalid sync frequency. Must be manual, daily, or weekly.'}), 400
    
    try:
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            user = User(email='default@neuroflow.app')
            db.session.add(user)
        
        user.sync_frequency = sync_frequency
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully',
            'sync_frequency': sync_frequency
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/history', methods=['GET'])
def get_oura_sync_history():
    """Get detailed sync history"""
    try:
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            return jsonify({'sync_history': []})
        
        # Get all sync logs for the user, ordered by most recent
        sync_logs = SyncLog.query.filter_by(user_id=user.id).order_by(SyncLog.started_at.desc()).all()
        
        history = []
        for sync in sync_logs:
            history.append({
                'id': sync.id,
                'sync_type': sync.sync_type,
                'status': sync.status,
                'start_date': sync.start_date.strftime('%Y-%m-%d') if sync.start_date else None,
                'end_date': sync.end_date.strftime('%Y-%m-%d') if sync.end_date else None,
                'records_imported': sync.records_imported,
                'error_message': sync.error_message,
                'started_at': sync.started_at.isoformat() if sync.started_at else None,
                'completed_at': sync.completed_at.isoformat() if sync.completed_at else None,
                'duration_seconds': (sync.completed_at - sync.started_at).total_seconds() if sync.completed_at and sync.started_at else None
            })
        
        return jsonify({
            'sync_history': history,
            'total_syncs': len(history),
            'successful_syncs': len([h for h in history if h['status'] == 'success']),
            'failed_syncs': len([h for h in history if h['status'] == 'failed'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/schedule', methods=['GET'])
def get_oura_schedule():
    """Get current sync schedule and status"""
    try:
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            return jsonify({
                'sync_enabled': False,
                'sync_frequency': 'manual',
                'last_automatic_sync': None,
                'next_scheduled_sync': None,
                'job_scheduled': False
            })
        
        status = oura_sync_manager.get_user_sync_status(user.id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/schedule', methods=['PUT'])
def update_oura_schedule():
    """Update sync schedule settings"""
    try:
        data = request.get_json()
        sync_enabled = data.get('sync_enabled', False)
        frequency = data.get('sync_frequency', 'manual')
        
        if frequency not in ['manual', 'daily', 'weekly']:
            return jsonify({'error': 'Invalid sync frequency. Must be manual, daily, or weekly.'}), 400
        
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            user = User(email='default@neuroflow.app')
            db.session.add(user)
        
        # Update sync settings using the manager
        success = oura_sync_manager.update_user_sync_settings(user.id, sync_enabled, frequency)
        
        if success:
            return jsonify({
                'message': 'Schedule updated successfully',
                'sync_enabled': sync_enabled,
                'sync_frequency': frequency
            })
        else:
            return jsonify({'error': 'Failed to update schedule'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/sync-automatic', methods=['POST'])
def trigger_automatic_sync():
    """Manually trigger automatic sync (for testing)"""
    try:
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            return jsonify({'error': 'User not found'}), 400
        
        if not user.sync_enabled:
            return jsonify({'error': 'Automatic sync is disabled'}), 400
        
        # Run the automatic sync
        result = oura_sync_manager.run_user_sync(user.id)
        
        if result.get('success'):
            return jsonify({
                'message': 'Automatic sync completed successfully',
                'records_imported': result.get('records_imported', 0),
                'start_date': result.get('start_date'),
                'end_date': result.get('end_date')
            })
        else:
            return jsonify({
                'error': result.get('error', 'Automatic sync failed'),
                'sync_log_id': result.get('sync_log_id')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/oura/sync-status', methods=['GET'])
def get_detailed_sync_status():
    """Get detailed sync status including automatic sync info"""
    try:
        user = User.query.filter_by(email='default@neuroflow.app').first()
        if not user:
            return jsonify({
                'has_token': False,
                'sync_enabled': False,
                'sync_frequency': 'manual',
                'last_sync': None,
                'last_automatic_sync': None,
                'next_scheduled_sync': None,
                'job_scheduled': False
            })
        
        # Get basic status
        basic_status = {
            'has_token': bool(user.oura_api_token),
            'token': '********************************' if user.oura_api_token else None,
            'last_sync': user.last_oura_sync.isoformat() if user.last_oura_sync else None,
            'sync_frequency': user.sync_frequency or 'manual',
        }
        
        # Get automatic sync status
        auto_status = oura_sync_manager.get_user_sync_status(user.id)
        
        # Combine the statuses
        combined_status = {**basic_status, **auto_status}
        
        return jsonify(combined_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graphs/<int:graph_id>', methods=['GET'])
def get_graph_details(graph_id):
    try:
        graph = Graph.query.get_or_404(graph_id)
        return jsonify({
            'id': graph.id,
            'name': graph.name,
            'description': graph.description,
            'is_temporary': graph.is_temporary,
            'tracked_metrics': graph.tracked_metrics
        })
    except Exception as e:
        return jsonify({'error': 'Graph not found'}), 404

@app.route('/api/graphs/<int:graph_id>', methods=['PUT'])
def update_graph_details(graph_id):
    try:
        graph = Graph.query.get_or_404(graph_id)
        data = request.get_json()
        
        if 'name' in data:
            graph.name = data['name']
        if 'description' in data:
            graph.description = data['description']
        if 'tracked_metrics' in data:
            graph.tracked_metrics = json.dumps(data['tracked_metrics'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Graph updated successfully',
            'graph': {
                'id': graph.id,
                'name': graph.name,
                'description': graph.description,
                'tracked_metrics': graph.tracked_metrics
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def convert_static_graph_to_tracked(graph_id):
    """Convert a static graph to use tracked metrics"""
    graph = Graph.query.get(graph_id)
    if not graph:
        return False
    
    # Get unique metrics from this graph's data points
    metrics = db.session.query(DataPoint.metric_name).filter_by(graph_id=graph_id).distinct().all()
    metrics_list = [metric[0] for metric in metrics]
    
    # Update graph to use tracked metrics
    graph.tracked_metrics = json.dumps(metrics_list)
    db.session.commit()
    
    return True

@app.route('/api/graphs/<int:graph_id>/convert-to-dynamic', methods=['POST'])
def convert_graph_to_dynamic(graph_id):
    try:
        success = convert_static_graph_to_tracked(graph_id)
        if success:
            return jsonify({'message': 'Graph converted to dynamic successfully'})
        else:
            return jsonify({'error': 'Graph not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/convert-all-graphs', methods=['POST'])
def convert_all_graphs_to_dynamic():
    try:
        graphs = Graph.query.filter_by(is_temporary=False).all()
        converted_count = 0
        
        for graph in graphs:
            if convert_static_graph_to_tracked(graph.id):
                converted_count += 1
        
        return jsonify({
            'message': f'Converted {converted_count} graphs to dynamic'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Experiment API endpoints
@app.route('/api/experiments', methods=['GET'])
def get_experiments():
    try:
        experiments = Experiment.query.order_by(Experiment.created_at.desc()).all()
        experiments_data = []
        
        for exp in experiments:
            experiments_data.append({
                'id': exp.id,
                'title': exp.title,
                'description': exp.description,
                'period': exp.period,
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'driver': exp.driver,
                'metric_of_interest': exp.metric_of_interest,
                'benchmark': exp.benchmark,
                'icon': exp.icon,
                'icon_color': exp.icon_color,
                'created_at': exp.created_at.isoformat(),
                'updated_at': exp.updated_at.isoformat()
            })
        
        return jsonify(experiments_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments', methods=['POST'])
def create_experiment():
    try:
        data = request.get_json()
        
        # Parse dates if they exist, otherwise auto-calculate
        start_date = None
        end_date = None
        
        if data.get('start_date') and data.get('end_date'):
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        elif data.get('period') and data['period'] != 'custom':
            # Auto-calculate dates based on period
            start_date, end_date = auto_calculate_dates(data['period'])
        
        experiment = Experiment(
            title=data['title'],
            description=data.get('description', ''),
            period=data['period'],
            start_date=start_date,
            end_date=end_date,
            driver=data.get('driver', ''),
            metric_of_interest=data['metric_of_interest'],
            benchmark=data['benchmark'],
            icon=data.get('icon'),
            icon_color=data.get('icon_color', '#3b82f6')
        )
        
        db.session.add(experiment)
        db.session.commit()
        
        return jsonify({
            'message': 'Experiment created successfully',
            'experiment': {
                'id': experiment.id,
                'title': experiment.title,
                'description': experiment.description,
                'period': experiment.period,
                'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
                'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
                'driver': experiment.driver,
                'metric_of_interest': experiment.metric_of_interest,
                'benchmark': experiment.benchmark,
                'icon': experiment.icon,
                'icon_color': experiment.icon_color,
                'created_at': experiment.created_at.isoformat(),
                'updated_at': experiment.updated_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>', methods=['GET'])
def get_experiment(experiment_id):
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        return jsonify({
            'id': experiment.id,
            'title': experiment.title,
            'description': experiment.description,
            'period': experiment.period,
            'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
            'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
            'driver': experiment.driver,
            'metric_of_interest': experiment.metric_of_interest,
            'benchmark': experiment.benchmark,
            'icon': experiment.icon,
            'icon_color': experiment.icon_color,
            'created_at': experiment.created_at.isoformat(),
            'updated_at': experiment.updated_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/experiments/<int:experiment_id>', methods=['PUT'])
def update_experiment(experiment_id):
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        data = request.get_json()
        
        # Parse dates if they exist, otherwise auto-calculate if period changed
        if data.get('start_date') and data.get('end_date'):
            experiment.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            experiment.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        elif 'period' in data and data['period'] != 'custom':
            # Auto-calculate dates if period is being updated
            start_date, end_date = auto_calculate_dates(data['period'])
            if start_date and end_date:
                experiment.start_date = start_date
                experiment.end_date = end_date
        
        # Update other fields
        if 'title' in data:
            experiment.title = data['title']
        if 'description' in data:
            experiment.description = data['description']
        if 'period' in data:
            experiment.period = data['period']
        if 'driver' in data:
            experiment.driver = data['driver']
        if 'metric_of_interest' in data:
            experiment.metric_of_interest = data['metric_of_interest']
        if 'benchmark' in data:
            experiment.benchmark = data['benchmark']
        if 'icon' in data:
            experiment.icon = data['icon']
        if 'icon_color' in data:
            experiment.icon_color = data['icon_color']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Experiment updated successfully',
            'experiment': {
                'id': experiment.id,
                'title': experiment.title,
                'description': experiment.description,
                'period': experiment.period,
                'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
                'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
                'driver': experiment.driver,
                'metric_of_interest': experiment.metric_of_interest,
                'benchmark': experiment.benchmark,
                'icon': experiment.icon,
                'icon_color': experiment.icon_color,
                'created_at': experiment.created_at.isoformat(),
                'updated_at': experiment.updated_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>', methods=['DELETE'])
def delete_experiment(experiment_id):
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        db.session.delete(experiment)
        db.session.commit()
        
        return jsonify({'message': 'Experiment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>/stats', methods=['GET'])
def get_experiment_stats(experiment_id):
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        # Get the metric of interest
        metric_name = experiment.metric_of_interest
        if not metric_name:
            return jsonify({
                'benchmark_value': None,
                'current_value': None,
                'improvement_percentage': None,
                'data_points_count': 0,
                'error': 'No metric specified'
            })
        
        # Calculate benchmark based on benchmark type
        benchmark_stats = calculate_benchmark(experiment)
        
        # Calculate current/post-experiment value if experiment has ended
        current_stats = calculate_current_value(experiment)
        
        # Calculate improvement percentage
        improvement_percentage = None
        if benchmark_stats['value'] is not None and current_stats['value'] is not None:
            if benchmark_stats['value'] != 0:
                improvement_percentage = ((current_stats['value'] - benchmark_stats['value']) / benchmark_stats['value']) * 100
            else:
                improvement_percentage = None
        
        return jsonify({
            'benchmark_value': benchmark_stats['value'],
            'current_value': current_stats['value'],
            'improvement_percentage': improvement_percentage,
            'data_points_count': benchmark_stats['count'],
            'benchmark_period': benchmark_stats['period'],
            'current_period': current_stats['period']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>/datapoints', methods=['GET'])
def get_experiment_datapoints(experiment_id):
    """Get data points for an experiment for completion review"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        # Get the metric of interest
        metric_name = experiment.metric_of_interest
        if not metric_name:
            return jsonify({
                'error': 'No metric specified for this experiment',
                'datapoints': []
            }), 400
        
        # Get data points during the experiment period
        query = DataPoint.query.filter(DataPoint.metric_name == metric_name)
        
        if experiment.start_date:
            query = query.filter(DataPoint.date >= experiment.start_date)
        
        if experiment.end_date:
            query = query.filter(DataPoint.date <= experiment.end_date)
        elif experiment.start_date:
            # If no end date but has start date, use up to today
            query = query.filter(DataPoint.date <= date.today())
        
        datapoints = query.order_by(DataPoint.date.asc()).all()
        
        # Format data points for frontend
        formatted_datapoints = []
        for dp in datapoints:
            formatted_datapoints.append({
                'date': dp.date.strftime('%Y-%m-%d'),
                'value': float(dp.value) if dp.value is not None else 0.0,
                'metric_name': dp.metric_name
            })
        
        return jsonify({
            'experiment_id': experiment_id,
            'experiment_title': experiment.title,
            'metric_name': metric_name,
            'datapoints': formatted_datapoints,
            'total_count': len(formatted_datapoints)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>/complete', methods=['POST'])
def complete_experiment(experiment_id):
    """Complete an experiment with selected data points"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        included_datapoints = data.get('included_datapoints', [])
        final_average = data.get('final_average')
        
        # Update experiment end date to today if not already set
        if not experiment.end_date:
            experiment.end_date = date.today()
        
        # Store completion data (you might want to add fields to track this)
        completion_data = {
            'completed_at': datetime.now().isoformat(),
            'included_datapoints_count': len(included_datapoints),
            'final_average': final_average,
            'excluded_datapoints_count': data.get('total_datapoints', len(included_datapoints)) - len(included_datapoints)
        }
        
        # You could store this in a new field if you add one to the model
        # For now, we'll just log it
        print(f"Experiment {experiment_id} completed: {completion_data}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Experiment completed successfully',
            'experiment_id': experiment_id,
            'completion_data': completion_data,
            'experiment': {
                'id': experiment.id,
                'title': experiment.title,
                'start_date': experiment.start_date.strftime('%Y-%m-%d') if experiment.start_date else None,
                'end_date': experiment.end_date.strftime('%Y-%m-%d') if experiment.end_date else None,
                'status': 'completed'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiments/<int:experiment_id>/table-data', methods=['GET'])
def get_experiment_table_data(experiment_id):
    """Get structured table data for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        # Get the metric of interest
        metric_name = experiment.metric_of_interest
        if not metric_name:
            return jsonify({
                'error': 'No metric specified for this experiment',
                'table_data': []
            }), 400
        
        # Calculate date range
        if experiment.start_date and experiment.end_date:
            start_date = experiment.start_date
            end_date = experiment.end_date
        elif experiment.start_date:
            # If only start date, use 7 days from start
            start_date = experiment.start_date
            end_date = start_date + timedelta(days=6)
        else:
            # If no dates, use next 7 days from today
            start_date = date.today()
            end_date = start_date + timedelta(days=6)
        
        # Calculate benchmark
        benchmark_stats = calculate_benchmark(experiment)
        benchmark_value = benchmark_stats['value']
        
        # Generate date range for table (7 days)
        table_dates = []
        current_date = start_date
        for i in range(7):
            if current_date <= end_date:
                table_dates.append(current_date)
                current_date += timedelta(days=1)
            else:
                # If we've reached the end date but need more dates, continue beyond
                table_dates.append(current_date)
                current_date += timedelta(days=1)
        
        # Get data points for the date range
        datapoints = DataPoint.query.filter(
            DataPoint.metric_name == metric_name,
            DataPoint.date >= start_date,
            DataPoint.date <= end_date
        ).all()
        
        # Create lookup for existing data points
        data_lookup = {dp.date: dp.value for dp in datapoints}
        
        # Build table data
        table_data = []
        for table_date in table_dates:
            value = data_lookup.get(table_date)
            has_data = value is not None
            
            # Calculate deviation if we have both value and benchmark
            deviation = None
            if has_data and benchmark_value is not None:
                deviation = value - benchmark_value
            
            table_data.append({
                'date': table_date.strftime('%Y-%m-%d'),
                'value': float(value) if has_data else None,
                'benchmark': float(benchmark_value) if benchmark_value is not None else None,
                'deviation': float(deviation) if deviation is not None else None,
                'has_data': has_data
            })
        
        return jsonify({
            'experiment_id': experiment_id,
            'experiment_title': experiment.title,
            'metric_name': metric_name,
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'benchmark_value': float(benchmark_value) if benchmark_value is not None else None,
            'table_data': table_data,
            'total_dates': len(table_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_benchmark(experiment):
    """Calculate benchmark value based on experiment settings"""
    try:
        metric_name = experiment.metric_of_interest
        benchmark_type = experiment.benchmark
        
        if benchmark_type == "avg-7-days":
            # Calculate 7-day average before experiment start
            if experiment.start_date:
                # Use experiment start date as reference point
                end_date = experiment.start_date
                start_date = end_date - timedelta(days=7)
            else:
                # If no start date, use last 7 days from today
                end_date = date.today()
                start_date = end_date - timedelta(days=7)
            
            # Query datapoints for the metric in the benchmark period
            datapoints = DataPoint.query.filter(
                DataPoint.metric_name == metric_name,
                DataPoint.date >= start_date,
                DataPoint.date < end_date
            ).all()
            
            if datapoints:
                values = [dp.value for dp in datapoints if dp.value is not None]
                avg_value = sum(values) / len(values) if values else None
                return {
                    'value': avg_value,
                    'count': len(values),
                    'period': f"{start_date} to {end_date}"
                }
            else:
                return {
                    'value': None,
                    'count': 0,
                    'period': f"{start_date} to {end_date}"
                }
        
        # Add other benchmark types here (avg-30-days, etc.)
        else:
            return {
                'value': None,
                'count': 0,
                'period': f"Unsupported benchmark: {benchmark_type}"
            }
            
    except Exception as e:
        return {
            'value': None,
            'count': 0,
            'period': f"Error: {str(e)}"
        }

def auto_calculate_dates(period):
    """Auto-calculate start and end dates based on period"""
    period_to_days = {
        '1-week': 7,
        '2-weeks': 14,
        '1-month': 30
    }
    
    days = period_to_days.get(period)
    if not days:
        return None, None
    
    # Start date is today
    start_date = date.today()
    # End date is start date + period days
    end_date = start_date + timedelta(days=days)
    
    return start_date, end_date

def calculate_current_value(experiment):
    """Calculate current/post-experiment value"""
    try:
        metric_name = experiment.metric_of_interest
        
        if experiment.start_date and experiment.end_date:
            # Use experiment period
            start_date = experiment.start_date
            end_date = experiment.end_date
        elif experiment.start_date:
            # Use from start date to today
            start_date = experiment.start_date
            end_date = date.today()
        else:
            # No dates set, return None
            return {
                'value': None,
                'count': 0,
                'period': 'No experiment dates set'
            }
        
        # Query datapoints for the metric during the experiment period
        datapoints = DataPoint.query.filter(
            DataPoint.metric_name == metric_name,
            DataPoint.date >= start_date,
            DataPoint.date <= end_date
        ).all()
        
        if datapoints:
            values = [dp.value for dp in datapoints if dp.value is not None]
            avg_value = sum(values) / len(values) if values else None
            return {
                'value': avg_value,
                'count': len(values),
                'period': f"{start_date} to {end_date}"
            }
        else:
            return {
                'value': None,
                'count': 0,
                'period': f"{start_date} to {end_date}"
            }
            
    except Exception as e:
        return {
            'value': None,
            'count': 0,
            'period': f"Error: {str(e)}"
        }

def create_plot_for_graph(graph_obj):
    """Create plot data for a graph object"""
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

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5174))
    app.run(debug=True, port=port)

