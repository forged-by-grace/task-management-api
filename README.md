# Task Management API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
6. [API Endpoints](#api-endpoints)
    - [User Authentication](#user-authentication)
    - [Task Management](#task-management)
7. [Testing](#testing)
8. [Logging](#logging)
9. [Dockerization](#dockerization)
10. [Continuous Integration (CI)](#continuous-integration-ci)

## Introduction <a name="introduction"></a>

This documentation provides detailed information about the Task Management API, which allows users to manage tasks within the system. The API includes endpoints for user authentication and task management.

## Installation <a name="installation"></a>

To install and run the Task Management API, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/forged-by-grace/task-management-api.git
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration <a name="configuration"></a>

The application configuration can be managed using Hydra configuration files located in the `config/` directory. There are separate configuration files for development, staging, and production environments.

## Database Setup <a name="database-setup"></a>

The application uses SQLite as the default database. 

## Running the Application <a name="running-the-application"></a>

To run the Task Management API, execute the following command:
```
python main.py [dev|staging|prod]
```

## API Endpoints <a name="api-endpoints"></a>

The authentication endpoints allow users to register, login, update their profile, and delete their account. Only authenticated users can access task management endpoints.

### API Version: v1

#### Register User Account

- **HTTP Method**: POST
- **Endpoint**: `/api/v1/accounts/register`
- **Description**: Register a new user with email and password.
- **Request Body**:
  ```json
  {
  "last_name": "James",
  "first_name": "Confidence",
  "username": "jc",
  "email": "joe@example.com",
  "avatar": "https://example.com/image.jpg",
  "password": "12345678"
  }
  ```
- **Response**: 
   ```json
  {
  "last_name": "James",
  "first_name": "Confidence",
  "username": "jc",
  "email": "joe@example.com",
  "avatar": "https://example.com/image.jpg",
  "id": 1,
  "is_active": false,
  "created_at": "2024-05-17T12:13:15",
  "updated_at": "2024-05-17T12:13:15",
  "role": "User"
  }
  ```
- **Status Codes**:
  - 200: Success
  - 400: Account with email already registered
  - 400: Account with username already registered
  - 422: Validation error

#### Login User

- **HTTP Method**: POST
- **Endpoint**: `/api/v1/accounts/login`
- **Description**: Login with registered email and password to obtain access token.
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "refresh_token": "string",
    "access_token": "string",
    "token_type": "string",
    "token_expiry_seconds": 3600,
    "data": {
      "first_name": "Confidence",
      "last_name": "James",
      "id": 0,
      "username": "jc",
      "email": "joe@example.com",
      "role": "Admin",
      "avatar": "https://example.com/image.jpg"
    }
  }
  ```
- **Status Codes**:
  - 200: Success  
  - 400: Invalid email
  - 400: Invalid password


#### Renew Access Token

- **HTTP Method**: GET
- **Endpoint**: `/api/v1/accounts/renew-access-token`
- **Description**: Get new access token with refesh token.
- **Request Header**:
  ```json
  {
    "authorization": "string",
    "x-refresh-token": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "refresh_token": "string",
    "access_token": "string",
    "token_type": "string",
    "token_expiry_seconds": 3600,
    "data": {
      "first_name": "Confidence",
      "last_name": "James",
      "id": 0,
      "username": "jc",
      "email": "joe@example.com",
      "role": "Admin",
      "avatar": "https://example.com/image.jpg"
    }
  }
  ```
- **Status Codes**:
  - 200: Success  
  - 401: Invalid credentials

#### Update Account

- **HTTP Method**: PUT
- **Endpoint**: `/api/v1/accounts/me`
- **Description**: Update user account profile.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Request Body**:
  ```json
  {
    "last_name": "string",
    "first_name": "string",
    "username": "string",
    "avatar": "string",
    "password": "string"
  }
  ```
- **Response**: Updated account details with email.
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized
  - 404: Not Found
  - 422: Validation error

#### Delete Account

- **HTTP Method**: DELETE
- **Endpoint**: `/api/v1/accounts/me`
- **Description**: Delete user account.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Response**: Deleted account details with email.
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized

#### Logout Account

- **HTTP Method**: DELETE
- **Endpoint**: `/api/v1/account/me`
- **Description**: Delete user account.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Response**: Logout successfully.
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized

## Task Management Endpoints

The task management endpoints allow authenticated users to perform CRUD operations on tasks.

### API Version: v1

#### Create Task

- **HTTP Method**: POST
- **Endpoint**: `/api/v1/tasks/create/`
- **Description**: Create a new task.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "start_time": "datetime",
    "stop_time": "datetime"
  }
  ```
- **Response**: 
  ```json
  {
    "title": "string",
    "description": "string",
    "start_time": "datetime",
    "stop_time": null,
    "id": "int",
    "completed": "boolean"
  }
  ```
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized
  - 422: Validation error

#### Get Tasks

- **HTTP Method**: GET
- **Endpoint**: `/api/v1/tasks/`
- **Description**: Get all tasks.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Response**: List of tasks.
  ```json
  [
    {
      "title": "string",
      "description": "string",
      "start_time": "datetime",
      "stop_time": null,
      "id": "int",
      "completed": "boolean"
    }
  ]
  ```
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized
  - 400: Not found

#### Get Task by ID

- **HTTP Method**: GET
- **Endpoint**: `/api/v1/tasks/{task_id}`
- **Description**: Get a task by ID.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Response**: Task details.
  ```json
  {
    "title": "string",
    "description": "string",
    "start_time": "datetime",
    "stop_time": null,
    "id": "int",
    "completed": "boolean"
  }
  ```
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized
  - 404: Task not found

#### Update Task

- **HTTP Method**: PUT
- **Endpoint**: `/api/v1/tasks/{task_id}`
- **Description**: Update a task by ID.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "completed": "boolean"
  }
  ```
- **Response**: Updated task details.
```json
  {
    "title": "string",
    "description": "string",
    "start_time": "datetime",
    "stop_time": null,
    "id": "int",
    "completed": "boolean"
  }
  ```
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized
  - 404: Task not found
  - 422: Validation error

#### Delete Task

- **HTTP Method**: DELETE
- **Endpoint**: `/api/v1/tasks/{task_id}`
- **Description**: Delete a task by ID.
- **Request Header**:
  ```json
  {
    "authorization": "string",
  }
  ```
- **Response**: Task deleted successfully.
- **Status Codes**:
  - 200: Success
  - 401: Unauthorized
  - 404: Task not found

## Testing <a name="testing"></a>

The application includes unit, integration, and end-to-end tests located in the `tests/` directory. To run the tests, use the following command:
```
pytest
```

## Logging <a name="logging"></a>

The application logs events and errors to the `log/audit.log` file.

## Dockerization <a name="dockerization"></a>

The application can be Dockerized using the provided `Dockerfile`. Build the Docker image using the following command:
```
docker build -t your_docker_image .
```

## Continuous Integration (CI) <a name="continuous-integration-ci"></a>

The application includes a Jenkinsfile for continuous integration. The Jenkinsfile is configured to build, test, and deploy the application according to the CI/CD pipeline requirements.