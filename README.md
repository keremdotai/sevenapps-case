# sevenapps-case

**Author :** Kerem Avci ([@keremdotmu](https://github.com/keremdotmu) and [@mkeremavci](https://github.com/mkeremavci))


## Table of Contents

1. [Project Overview](#project-overview)
2. [Requirements](#requirements)
3. [Environment Variables](#environment-variables)
4. [Build the Application](#build-the-application)
5. [Run the Application](#run-the-application)
6. [Accessing Logs](#accessing-logs)
7. [API Documentation](#api-documentation)
8. [Testing](#testing)


## Project Overview

In this project, it is supposed to implement a chatbot communicating with the user via an API.
This chatbot receives a PDF file and enables user to talk on the file's content.

The system only accepts PDF files with text content.
If the file only consists of images and requires OCR to extract text content,
the server throws error and returns 400 Bad Request.

The file's text content and metadata are stored in MongoDB database.
This database also provides a collection for storing logs.
The main part of the logging system is built on this database.

Moreover, Redis database serves as a cache for storing chat history. The cache stores a number of messages predeterimened in `.env` file with `REDIS_LIST_LIMIT`. This includes the chat bot's responses.


## Requirements

The softwares and tools required to build and run the project are given below:

- Docker


## Environment Variables

Before building and running the project, you must provide **.env** file inside the main directory of project. You can copy the content of **.env.template** file and replace values with actual ones.

```bash
cp .env.template .env
nano .env
```

Descriptions of the environment variables are given in **.env.template** file. Please consider them before assigning values.


## Build the Application

> [!IMPORTANT] 
>
> You must create folders that will be used as volumes for MongoDB and Redis databases. If you set `MONGODB_VOLUME` and `REDIS_VOLUME` variables in **.env** file with proper paths, you can create folders with the following command;
> ```bash
> source .env && mkdir -p ${MONGODB_VOLUME} ${REDIS_VOLUME}
> ```
> Otherwise, you should create folders manually.
>

You can build the application with the following command;

```bash
docker compose build
```


## Run the Application

You can run the application with the following command;

```bash
docker compose up -d
```

The server would wait till the health check of the database containers completes with success.

## Accessing Logs

You can access the logs of all events by using [MongoDB Compass](https://www.mongodb.com/products/tools/compass). The connection string is given below:

    mongodb://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@localhost:${MONGODB_PORT}/

You can access uvicorn logs with the following command;

```bash
docker compose logs -f
```


## API Documentation

### Upload PDF

```http
POST /v1/pdf
```

#### Request

Uploads a PDF file to be processed. The file should be included in the form data.

##### CURL example

```bash
curl -X POST "http://localhost:${SERVER_PORT}/v1/pdf" \
    -F "file=@/path/to/your/pdf/file.pdf"
```

##### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `file` | `file` | **Required.** The PDF file to upload. |

#### Responses

##### Success Response

**Code :** 201 CREATED

**Content :**

```json
{
    "pdf_id": "unique_pdf_identifier"
}
```

##### Error Responses

**Code :** 499 CLIENT CLOSED REQUEST

**Content :**

```json
{
    "detail": "Client disconnected"
}
```

**Code :** 413 PAYLOAD TOO LARGE

**Content :**

```json
{
    "detail": "Request body size exceeded ${MAX_SIZE} bytes (${RECEIVED_BYTES} bytes received)"
}
```

**Code :** 400 BAD REQUEST

**Content :**

```json
{
    "detail": "Invalid file data"
}
```

**Code :** 500 INTERNAL SERVER ERROR

**Content :**

```json
{
    "detail": "Failed to parse PDF file, please check the file content/format"
}
```

or

```json
{
    "detail": "Failed to insert PDF document into the database"
}
```

### Chat with Bot on PDF Content

```http
POST /v1/chat/{pdf_id}
```

#### Request

Sends a message to the chatbot to inquire about the content of the uploaded PDF identified by `pdf_id`.

##### CURL example

```bash
curl -X POST "http://localhost:8000/v1/chat/{pdf_id}" \
    -H "Content-Type: application/json" \
    -d '{"message": "What is the main topic of this PDF?"}'
```

##### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `pdf_id` | `string` | **Required.** The unique identifier of the PDF obtained from the upload endpoint. |
| `message` | `string` | **Required.** The question you want to ask the chatbot about the PDF content. |

#### Responses

##### Success Response

**Code :** 200 OK

**Content :**

```json
{
    "response": "The main topic of this PDF is ."
}
```

##### Error Responses

**Code :** 400 BAD REQUEST

**Content :**

```json
{
    "detail": "Invalid request body"
}
```

**Code :** 404 NOT FOUND

**Content :**

```json
{
    "detail": "PDF not found"
}
```

**Code :** 500 INTERNAL SERVER ERROR

**Content :**

```json
{
    "detail": "Failed to chat with the bot"
}
```


## Testing

> [!WARNING]
>
> The program is written with **Python 3.11**.
> Please create a virtual environment in Python 3.11 before stepping into the next steps.
> Besides, for database and router tests, there must be Docker engine to run.
>

> [!IMPORTANT]
>
> Before running the tests, you must install the requirements given in `app/requirements.txt`
> and `python-dotenv` package. You can install the requirements with the following lines:
>
> ```bash
> python -m pip install -r app/requirements.txt
> python -m pip install python-dotenv
> ```
>

Test cases are provided inside `app/tests` folder. You can run all tests together with the following command:

```bash
python app/tests --all
```

If you want to run specific test cases, you can only run them with the following command:

```bash
python app/tests name_of_case_1 name_of_case_2 ...
```
You can call test cases individually with the names below:

- utils
- nlp
- database
- routers

The test results are written in JSON format to `app/tests/results` folder.
