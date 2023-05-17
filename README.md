# Social Media Application Backend
This is the backend for a social media application. It provides API endpoints to create users, manage friend requests, search for users, and enforce rate limits on friend requests. This document provides instructions on how to set up and run the application using Docker and how to test the APIs using the provided Postman collection.

## Prerequisites
Before running the application, please ensure that you have the following software installed on your system:

1. Docker: The application is containerized using Docker, so make sure Docker is installed and running on your machine.
https://docs.docker.com/engine/install/

## Getting Started
To get the server up and running, follow these steps:
1. Clone the repository
2. Navigate to the project directory
3. Build and start the Docker containers: docker-compose up
4. Once the containers are up and running, the server should be accessible at http://localhost:8000.

## Testing the APIs
To test the APIs, you can import the provided Postman collection into Postman. The collection includes pre-configured requests with example payloads and expected responses.

## Rate Limiting
The application enforces a rate limit of 3 friend requests per minute for each user. If a user exceeds this limit, they will receive an appropriate error response.
