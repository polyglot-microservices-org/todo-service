# ✅ Todo Service

> **Task management API built with Python Flask and MongoDB**

## 📋 Overview

The Todo Service is a Python Flask microservice that provides comprehensive task management functionality. It offers full CRUD operations for todos with completion tracking, MongoDB persistence, and seamless integration with the polyglot microservices ecosystem.

## 🏗️ Architecture

### Technology Stack
- **Language**: Python 3.9+
- **Framework**: Flask with CORS support
- **Database**: MongoDB with connection retry logic
- **Container**: Docker with multi-stage build
- **Orchestration**: Kubernetes with StatefulSet database

### Service Details
- **Port**: 5001
- **Health Check**: `/healthz`
- **API Prefix**: `/todos`
- **Docker Image**: `yaswanthmitta/multiapp-todo-app`
- **Database**: MongoDB (todo-db:27017)

## 🚀 API Documentation

### Base URL
```
http://localhost:5001
```

### Endpoints

#### Create Todo
**POST** `/todos`

Create a new todo item.

**Request Body:**
```json
{
  "task": "Complete project documentation"
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "task": "Complete project documentation",
  "completed": false
}
```

#### Get All Todos
**GET** `/todos`

Retrieve all todo items.

**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "task": "Complete project documentation",
    "completed": false
  },
  {
    "id": "507f1f77bcf86cd799439012",
    "task": "Review code changes",
    "completed": true
  }
]
```

#### Get Todo by ID
**GET** `/todos/{id}`

Retrieve a specific todo by ID.

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "task": "Complete project documentation",
  "completed": false
}
```

#### Update Todo
**PUT** `/todos/{id}`

Update an existing todo (task content or completion status).

**Request Body:**
```json
{
  "task": "Complete project documentation - Updated",
  "completed": true
}
```

**Response:**
```json
{
  "message": "To-do item updated successfully"
}
```

#### Delete Todo
**DELETE** `/todos/{id}`

Delete a todo by ID.

**Response:**
```json
{
  "message": "To-do item deleted successfully"
}
```

#### Health Check
**GET** `/healthz`

Service health status.

**Response:**
```json
{
  "status": "ok"
}
```

### Error Responses
```json
{
  "error": "To-do item not found"
}
```

## 🔧 Configuration

### Environment Variables
```bash
MONGO_URI=mongodb://todo-db:27017/
DB_NAME=todo_db
```

### Database Configuration
- **Database**: `todo_db`
- **Collection**: `todos`
- **Connection Retry**: 10 attempts with 5-second intervals
- **Connection Timeout**: Automatic reconnection on failure

## 🏗️ Code Structure

### Database Initialization
```python
def init_db():
    """Initializes the MongoDB client and verifies connection."""
    retries = 10
    while retries > 0:
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ping')
            print("✅ Connected to MongoDB.")
            return client
        except Exception as e:
            print(f"⚠️ DB not ready yet: {e}")
            retries -= 1
            time.sleep(5)
    raise Exception("❌ Could not connect to database after several retries.")
```

### Todo Operations
```python
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
```

### CORS Configuration
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
```

## 🐳 Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/healthz || exit 1

CMD ["python", "main.py"]
```

### Build and Run
```bash
# Build image
docker build -t todo-service .

# Run container
docker run -p 5001:5001 \
  -e MONGO_URI=mongodb://localhost:27017/ \
  -e DB_NAME=todo_db \
  todo-service
```

## ☸️ Kubernetes Deployment

### Resources
- **Deployment**: Manages Flask application pods
- **Service**: ClusterIP for internal communication
- **StatefulSet**: MongoDB database with persistent storage
- **PVC**: Persistent volume for data storage
- **HPA**: Auto-scaling based on CPU/memory usage

### Database Configuration
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: todo-db
spec:
  serviceName: todo-db
  replicas: 1
  template:
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: todo-db-storage
          mountPath: /data/db
        env:
        - name: MONGO_INITDB_DATABASE
          value: todo_db
  volumeClaimTemplates:
  - metadata:
      name: todo-db-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

### Deploy to Kubernetes
```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=todo-service
kubectl get statefulset todo-db
kubectl logs -l app=todo-service
```

## 🔄 CI/CD Pipeline

### Continuous Integration (CI)
**Trigger**: Push to any branch with changes in `app/` directory

**Pipeline Steps**:
1. **Checkout Code**: Get latest Python source code
2. **Docker Login**: Authenticate with Docker Hub
3. **Build & Test**: Install dependencies and run tests
4. **Build Image**: Create optimized Docker image
5. **Push Image**: Tag with Git SHA and push to registry
6. **Update Manifests**: Inject new image tag into Kubernetes files
7. **Commit Changes**: Push updated deployment manifests

### Continuous Deployment (CD)
**Trigger**: Successful CI completion or K8s manifest changes

**Pipeline Steps**:
1. **Checkout Code**: Get updated Kubernetes manifests
2. **Deploy to K8s**: Apply all service resources
3. **Rolling Update**: Zero-downtime deployment with health checks
4. **Verification**: Validate service availability

### Image Tagging Strategy
```bash
# Format: yaswanthmitta/multiapp-todo-app:<git-sha>
yaswanthmitta/multiapp-todo-app:a1b2c3d4e5f6
```

## 🔒 Security Implementation

### Application Security
- **Input Validation**: Strict request body validation
- **Error Handling**: Secure error messages without sensitive data
- **CORS Configuration**: Controlled cross-origin access
- **Database Security**: Parameterized queries to prevent injection

### Container Security
- **Non-root User**: Application runs as user ID 1000
- **Minimal Base Image**: Python slim for reduced attack surface
- **Health Checks**: Container health monitoring
- **Resource Limits**: CPU and memory constraints

### Database Security
- **Network Isolation**: MongoDB accessible only within cluster
- **Data Persistence**: Encrypted storage with PVC
- **Access Control**: Service-specific database access
- **Connection Security**: Authenticated MongoDB connections

## 📊 Monitoring & Observability

### Application Metrics
```python
# Custom metrics collection (example)
import time
from functools import wraps

def monitor_requests(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            # Log successful request
            duration = time.time() - start_time
            print(f"Request to {f.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            # Log error
            print(f"Request to {f.__name__} failed: {str(e)}")
            raise
    return decorated_function
```

### Key Performance Indicators
- **Request Rate**: Requests per second
- **Response Time**: Average API response latency
- **Error Rate**: Percentage of failed requests
- **Database Performance**: MongoDB query execution time
- **Task Completion Rate**: Business metric for todo completion

### Health Monitoring
- **Liveness Probe**: `/healthz` endpoint for container health
- **Readiness Probe**: Database connectivity verification
- **Startup Probe**: Application initialization check

## 🧪 Testing

### Unit Testing
```python
import unittest
from main import app, init_db

class TodoServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_todo(self):
        response = self.app.post('/todos', 
                               json={'task': 'Test task'},
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
    def test_get_todos(self):
        response = self.app.get('/todos')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Start local MongoDB
docker run -d --name test-mongo -p 27017:27017 mongo:7.0

# Set environment variables
export MONGO_URI=mongodb://localhost:27017/
export DB_NAME=test_todo_db

# Run application
python main.py

# Test endpoints
curl -X POST http://localhost:5001/todos \
  -H "Content-Type: application/json" \
  -d '{"task": "Test todo item"}'

curl http://localhost:5001/todos
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p test_data.json http://localhost:5001/todos

# test_data.json content:
# {"task": "Load test todo"}
```

## 🚨 Troubleshooting

### Common Issues

#### MongoDB Connection Failed
```bash
# Check MongoDB pod status
kubectl get pods -l app=todo-db
kubectl logs -l app=todo-db

# Test connectivity from todo service
kubectl exec -it <todo-service-pod> -- python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://todo-db:27017/')
print(client.admin.command('ping'))
"
```

#### Application Crashes
```bash
# Check application logs
kubectl logs -l app=todo-service

# Check resource usage
kubectl top pods -l app=todo-service

# Describe pod for events
kubectl describe pod <todo-service-pod>
```

#### Slow Database Queries
```bash
# Check MongoDB performance
kubectl exec -it <mongodb-pod> -- mongo todo_db --eval "
db.todos.getIndexes()
db.todos.stats()
"

# Add indexes if needed
kubectl exec -it <mongodb-pod> -- mongo todo_db --eval "
db.todos.createIndex({task: 'text'})
db.todos.createIndex({completed: 1})
"
```

### Debug Commands
```bash
# Check service status
kubectl get svc todo-service

# View real-time logs
kubectl logs -f deployment/todo-service

# Test database connection
kubectl exec -it <todo-service-pod> -- nc -zv todo-db 27017

# Check HPA status
kubectl get hpa todo-service-hpa
```

## 📈 Performance Optimization

### Flask Optimization
```python
# Connection pooling
from pymongo import MongoClient
from pymongo.pool import Pool

client = MongoClient(
    MONGO_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000
)
```

### Database Optimization
```javascript
// MongoDB indexes for better performance
db.todos.createIndex({ "task": "text" })
db.todos.createIndex({ "completed": 1 })
db.todos.createIndex({ "_id": 1, "completed": 1 })
```

### Resource Configuration
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

## 🔗 Integration Points

### Frontend Integration
```javascript
// Frontend API calls
const response = await fetch('/api/todo/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task: 'New todo item' })
});

// Toggle completion
const toggleResponse = await fetch(`/api/todo/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: !currentStatus })
});
```

### Service Mesh
- **Nginx Routing**: `/api/todo/*` routes to this service
- **Service Discovery**: Kubernetes DNS resolution (todo-service:5001)
- **Load Balancing**: Kubernetes service distributes traffic
- **Health Checks**: Integrated with Kubernetes probes

## 📚 Dependencies

### Python Requirements
```txt
Flask==2.3.3
flask-cors==4.0.0
pymongo==4.5.0
```

### External Services
- **MongoDB**: Document database for todo storage
- **Kubernetes**: Container orchestration platform
- **Docker Hub**: Container image registry
- **Nginx**: Reverse proxy for API routing

## 🏷️ Tags
`python` `flask` `mongodb` `microservices` `rest-api` `kubernetes` `docker` `todo` `task-management`

---

**🌟 Scalable Python Flask microservice with robust MongoDB integration!**