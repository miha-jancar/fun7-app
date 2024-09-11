# fun7-app
docker build -t connectivity-test .

docker run -p 5000:5000 -d flask-connectivity-test

curl -X POST http://localhost:5000/test-endpoints -H "Content-Type: application/json" -d '{
  "endpoints": [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://httpbin.org/delay/1",
    "https://api.github.com"
  ]
}'

