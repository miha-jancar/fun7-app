# Fun7 Connectivity Test Server (CTS)

## Project Overview
A backend service for the Fun7 mobile game that checks server latency and helps the game decide the best backend to connect to.

## Tech Stack
- Language: Python
- CI/CD: GitHub Actions
- Containerization: Docker
- Infrastructure: Google Cloud (Cloud Run/GKE)
- IaC: Terraform
- Authentication: Since service is publicly exposed I've added authentication with API Key. For more sufisticated authentication I would rather implement Oauth approach 

## How to Build and Run Locally
```bash
docker build -t cts-server .
docker run -p 5000:5000 -p 8000:8000 cts-server
```

## How to access service in Google Cloud

```
curl -X POST https://fun7-cts-398084804535.europe-west3.run.app/test-endpoints  -H "x-api-key: <provided separately>" -H "Content-Type: application/json" -d '{
  "endpoints": [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://httpbin.org/delay/1",
    "https://api.github.com"
  ]
}'
```

##  Expected result

```
{"best_endpoint":"https://api.github.com","latencies":{"https://api.github.com":0.06144523620605469,"https://httpbin.org/delay/1":1.4082317352294922,"https://jsonplaceholder.typicode.com/todos/1":0.11386847496032715}}
```
