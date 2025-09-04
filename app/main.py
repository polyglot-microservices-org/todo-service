import os
import time
from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB configuration from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://todo-db:27017/")
DB_NAME = os.getenv("DB_NAME", "todo_db")

def init_db():
    """Initializes the MongoDB client and verifies connection."""
    retries = 10
    while retries > 0:
        try:
            client = MongoClient(MONGO_URI)
            # The ping command is a lightweight way to check the connection.
            client.admin.command('ping')
            print("✅ Connected to MongoDB.")
            return client
        except Exception as e:
            print(f"⚠️ DB not ready yet: {e}")
            retries -= 1
            time.sleep(5)
    raise Exception("❌ Could not connect to database after several retries.")

# Initialize DB client and get database object on startup
mongo_client = init_db()
db = mongo_client[DB_NAME]

@app.route('/todos', methods=['POST'])
def create_todo():
    """Creates a new todo item."""
    data = request.json
    if not data or 'task' not in data:
        return jsonify({'error': 'Missing "task" field'}), 400

    task = data['task']
    try:
        todos = db.todos
        result = todos.insert_one({'task': task, 'completed': False})
        return jsonify({
            'id': str(result.inserted_id),
            'task': task,
            'completed': False
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos', methods=['GET'])
def get_all_todos():
    """Gets all todo items."""
    try:
        todos = db.todos
        all_todos = list(todos.find({}))
        # Convert ObjectId to string for JSON serialization
        for todo in all_todos:
            todo['id'] = str(todo['_id'])
            del todo['_id']
        return jsonify(all_todos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Gets a single todo by ID."""
    try:
        todos = db.todos
        todo = todos.find_one({'_id': ObjectId(todo_id)})
        if todo:
            todo['id'] = str(todo['_id'])
            del todo['_id']
            return jsonify(todo)
        return jsonify({'error': 'To-do item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Updates an existing todo."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    update_fields = {}
    if 'task' in data:
        update_fields['task'] = data['task']
    if 'completed' in data:
        update_fields['completed'] = data['completed']

    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400

    try:
        todos = db.todos
        result = todos.update_one({'_id': ObjectId(todo_id)}, {'$set': update_fields})
        if result.modified_count == 0:
            return jsonify({'error': 'To-do item not found or no changes made'}), 404
        return jsonify({'message': 'To-do item updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Deletes a todo by ID."""
    try:
        todos = db.todos
        result = todos.delete_one({'_id': ObjectId(todo_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'To-do item not found'}), 404
        return jsonify({'message': 'To-do item deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint for Kubernetes probes
@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
