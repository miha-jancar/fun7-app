from flask import Flask, request, jsonify, Response
import requests
import time
import logging
from prometheus_client import Summary, Counter, generate_latest, CONTENT_TYPE_LATEST

# Initialize the Flask application
app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Log level
    format='%(asctime)s [%(levelname)s] %(message)s',  # Log format
    handlers=[
        logging.StreamHandler()  # Logs to standard output (stdout)
    ]
)

# Prometheus metrics
REQUEST_LATENCY = Summary('request_latency_seconds', 'Latency of HTTP requests in seconds')
REQUEST_COUNT = Counter('request_count', 'Total number of HTTP requests')

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

@app.route('/metrics')
def metrics():
    """
    Expose Prometheus metrics on the same port.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    # Log that the application is starting
    logging.info("Starting Flask app and serving Prometheus metrics on the same port...")

    # Run Flask server (host 0.0.0.0 to make it accessible outside Docker)
    app.run(host='0.0.0.0', port=5000)

