from flask import Flask, request, jsonify, Response, abort
import os
import requests
import time
import logging
from prometheus_client import Summary, Counter, generate_latest, CONTENT_TYPE_LATEST
from threading import Thread


# Initialize the Flask application for the main app
app = Flask(__name__)

# Separate Flask app for Prometheus metrics
metrics_app = Flask('metrics_app')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Prometheus metrics
REQUEST_LATENCY = Summary('request_latency_seconds', 'Latency of HTTP requests in seconds')
REQUEST_COUNT = Counter('request_count', 'Total number of HTTP requests')

# Load API Key from environment variables (or fallback to a default value if not set)
API_KEY = os.getenv('API_KEY')

def check_api_key(api_key):
    """
    Check if the provided API key is valid.
    """
    return api_key == API_KEY

def require_api_key(func):
    """
    Decorator that requires a valid API key in the request headers.
    """
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or not check_api_key(api_key):
            abort(401, description="Unauthorized: Invalid or missing API key")
        return func(*args, **kwargs)
    return decorated_function

def measure_latency(endpoint):
    """
    Measure the latency of a request to the given endpoint.
    """
    try:
        start_time = time.time()
        logging.info("Sending request to {}".format(endpoint))
        response = requests.get(endpoint, timeout=5)  # timeout after 5 seconds
        response.raise_for_status()  # raise error for non-2xx responses
        latency = time.time() - start_time
        logging.info("Request to {} completed successfully in {:.4f} seconds".format(endpoint, latency))
        return latency
    except requests.exceptions.RequestException as e:
        logging.error("Error measuring latency for {}: {}".format(endpoint, e))
        return float('inf')  # return infinity if the request fails

@app.route('/test-endpoints', methods=['POST'])
@require_api_key  # Require API key for this endpoint
@REQUEST_LATENCY.time()  # Track latency for this endpoint
def test_endpoints():
    """
    Accepts 3 endpoints via POST and returns the one with the lowest latency.
    """
    REQUEST_COUNT.inc()  # Increment the request count

    data = request.json
    logging.info("Received request to test endpoints: {}".format(data))

    if not data or 'endpoints' not in data or len(data['endpoints']) != 3:
        logging.error("Invalid input. Expected 3 endpoints.")
        return jsonify({'error': 'Please provide exactly 3 endpoints.'}), 400

    endpoints = data['endpoints']
    latencies = {}

    # Measure the latency for each endpoint
    for endpoint in endpoints:
        latencies[endpoint] = measure_latency(endpoint)

    # Find the endpoint with the lowest latency
    best_endpoint = min(latencies, key=latencies.get)

    logging.info("Best endpoint: {} with latencies: {}".format(best_endpoint, latencies))
    return jsonify({
        'best_endpoint': best_endpoint,
        'latencies': latencies
    })

@metrics_app.route('/metrics')
@require_api_key  # Require API key for the metrics endpoint
def metrics():
    """
    Expose Prometheus metrics on a separate port.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def run_metrics_server():
    """
    Run the Prometheus metrics Flask app on a separate thread and port.
    """
    metrics_app.run(host='0.0.0.0', port=8000)  # Expose metrics on port 8000

if __name__ == '__main__':
    # Start the Prometheus metrics server on a separate thread
    metrics_thread = Thread(target=run_metrics_server)
    metrics_thread.start()

    # Log that the application is starting
    logging.info("Starting Flask app...")

    # Run Flask server (host 0.0.0.0 to make it accessible outside Docker)
    app.run(host='0.0.0.0', port=5000)

