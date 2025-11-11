<div align="center">
  <a href="#">
    <picture>
      <source srcset="assets/img/iconbot-dark.png" media="(prefers-color-scheme: dark)">
      <source srcset="assets/img/iconbot-light.png" media="(prefers-color-scheme: light)">
      <img src="assets/img/iconbot-light.png" width="520" alt="AVRI logo">
    </picture>
  </a>
</div>

# AVRI-Back [![Coverage Status](https://coveralls.io/repos/github/MikelBarajas38/AVRI-Back/badge.svg?kill_cache=1)](https://coveralls.io/github/MikelBarajas38/AVRI-Back)
![Dockerized](https://img.shields.io/badge/docker-compose-blue)
![Django](https://img.shields.io/badge/django-4.2%20%7C%205.0-0C4B33)
![Python](https://img.shields.io/badge/python-3.12%20-blue)

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [RAGFlow Configuration](#ragflow-configuration)
- [Running AVRI](#running-avri)
- [Verification](#verification)
- [RAGFlow Setup](#ragflow-setup)
- [Testing](#testing)
- [Stopping AVRI](#stopping-avri)
- [Additional Notes](#additional-notes)
- [Contribution](#contribution)

---

## Introduction

AVRI-Back is the backend system that powers AVRI (Asistente Virtual del Repositorio Institucional), an AI-powered virtual assistant designed to help users navigate and interact with institutional repositories. The system uses RAGFlow for document processing and retrieval-augmented generation capabilities.

---

## Prerequisites

Before starting, ensure you have the following installed:
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) and Docker Compose
- [RAGFlow](https://ragflow.io/)

### Hardware Requirements

The following minimum hardware specifications are required for optimal performance:

- **RAM**: At least 8GB
- **CPU**: Intel i3 10th generation or equivalent
- **Storage**: Approximately 50GB of free space

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MikelBarajas38/AVRI-Back.git
```

### 2. Navigate to the Project Directory

```bash
cd AVRI-Back
```

---

## RAGFlow Configuration

> **Important**: RAGFlow must be running before starting AVRI-Back.

### 1. Initialize RAGFlow

Navigate to the folder where RAGFlow is installed and run:

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 2. Check RAGFlow Logs

```bash
docker logs -f ragflow-server
```

### 3. Verify Successful Startup

If everything executed correctly, you should see:
- The RAGFlow logo in ASCII art
- The "TASK EXECUTOR" message

![RAGFlow Success](https://github.com/user-attachments/assets/284a1b31-379a-4779-853d-7cedecfde258)

---

## Running AVRI

Once RAGFlow is running, start AVRI-Back with the following command:

```bash
docker compose -f docker-compose.yml -f docker-compose.ragflow.yml up
```

This command will initialize all necessary containers.

---

## Verification

### Successful Startup Logs

If the execution is successful, you should see logs similar to these:

![Success Logs](https://github.com/user-attachments/assets/93ffcfc4-c321-4117-8f88-5e010f870925)

### Service Status

You can verify the container status with:

```bash
docker ps
```

---

## RAGFlow Setup

### Initial Configuration

For chat and embedding functionality, it is recommended to use local models. However, if needed, you can use an API key from your preferred provider. Google's Gemini offers free API keys with a limited token quota at [https://aistudio.google.com/api-keys](https://aistudio.google.com/api-keys).

### Account Creation

If this is your first time using RAGFlow, create an account at:

```
http://localhost/login
```

### Creating Assistants

After creating your account, log in and navigate to the chats view:

```
http://localhost/chat
```

Click the "Create an Assistant" button.

![Create Assistant](assets/img/CreateAss.png)

You will need to create two different assistants:
1. One for "Titles"
2. One for "Chats"

#### RAGFLOW_TITLER

Create the first assistant named "Titler system prompt" with the following opening greeting:

```
Respuesta en base a documentos
```

In the **Prompt Engine** section, add the following text in the **System Prompt** field:

```bash
Eres un asistente experto en generar títulos breves y descriptivos para conversaciones.
 
Tu tarea es leer la primera consulta del usuario y generar un título claro, conciso y representativo del tema principal de la conversación.
 
El título debe tener entre 3 y 8 palabras, sonar natural, y poder usarse como nombre para un chat.
 
No incluyas signos de puntuación innecesarios, no respondas con frases completas, ni expliques tu elección. Solo devuelve el título sugerido.
 
Ignora saludos, despedidas o palabras genéricas como “hola”, “quiero”, “ayuda con”, etc.
 
Aquí está una base de conocimientos que puede ayudarte:
 
{knowledge}
 
Aquí termina la base de conocimientos
```

Click "Ok" to save. After creating the assistant, select it and locate the `dialogId` parameter in the URL. Copy this value and add it to your `.env` file as the `RAGFLOW_TITLER_ID` variable.

![Create Assistant](assets/img/TitlerId.png)

#### RAGFLOW_ASSISTANT

Create the second assistant named "AVRI System prompt" with the following opening greeting:

```
Hola, ¿Cómo te puedo ayudar?
```

In the **Prompt Engine** section, add the following text in the **System Prompt** field:

```bash
Eres un asistente virtual útil y conocedor del repositorio institucional de una universidad. Tu tarea es interactuar de manera natural con los usuarios y ayudarlos a encontrar los documentos o información más relevantes disponibles en la base de conocimientos.
 
Utiliza el contenido recuperado para recomendar documentos específicos, resumir secciones relevantes o responder directamente con base en los datos del repositorio. Personaliza tus respuestas considerando el perfil del usuario y el historial de conversación, incluyendo su tipo (por ejemplo: alumno, autor o administrador).
 
Si la base de conocimientos no contiene información relevante para responder a la pregunta, debes indicar explícitamente: "La respuesta que buscas no se encuentra en la base de conocimientos."
 
No inventes respuestas ni salgas del contenido recuperado. Prioriza siempre la claridad, la relevancia y las recomendaciones respaldadas por documentos. Recuerda no utilizar estilos en los mensajes, y solo deja la respuesta en texto plano.
 
      Here is the knowledge base:
      {knowledge}
      The above is the knowledge base.
```

Click "Ok" to save. After creating the assistant, select it and locate the `dialogId` parameter in the URL. Copy this value and add it to your `.env` file as the `RAGFLOW_ASSISTANT_ID` variable.

![Create Assistant](assets/img/AssitantId.png)

#### DATASET_ID

Create a new knowledge database from the knowledge section by clicking "Create knowledge base":

```
http://localhost/knowledge
```

Select the knowledge base and locate the `dataset?id` parameter in the URL. Copy this ID and add it to your `.env` file as the `DATASET_ID` variable.

![Create Assistant](assets/img/Knowledge.png)


#### RAGFLOW_API_KEY

To obtain the RAGFlow API Key, navigate to the API section in user settings:

```
http://localhost/user-setting/api
```

Click the "API KEY" button, then "Create new Key" (if needed). Copy the generated key and add it to your `.env` file as the `RAGFLOW_API_KEY` variable.

#### Other Environment Variables

Add the following variables to your `.env` file:

- `RI_BASE_URL=https://repositorioinstitucional.uaslp.mx/`
- `RI_BASE_URL_REST=https://repositorioinstitucional.uaslp.mx/rest`
- `RAGFLOW_BASE_URL=http://ragflow-server:9380/api/v1`

### Complete .env Example

Your `.env` file should look similar to this:

```bash
GEMINI_API_KEY=Bd...ff
RAGFLOW_API_KEY=ragflow-df...gj
RAGFLOW_BASE_URL=http://ragflow-server:9380/api/v1
RAGFLOW_ASSISTANT_ID=sd...6f
RAGFLOW_TITLER_ID=54...sd
DATASET_ID=sf...fd
RI_BASE_URL=https://repositorioinstitucional.uaslp.mx/
RI_BASE_URL_REST=https://repositorioinstitucional.uaslp.mx/rest
```

---

## Testing

The test suite covers (but is not limited to) the following components:
- Management Commands
- API Endpoints
- Core Models & Data
- Authentication & User Management

### Running Tests

To run the tests and view the coverage report:

```bash
docker compose run --rm app sh -c "coverage run --source='.' manage.py test && coverage report"
```

---

## Stopping AVRI

### Method 1: Manual Interruption

1. Press `Ctrl + C` in the terminal where the containers are running
2. Execute the following command to ensure all services stop:

```bash
docker compose down
```

### Method 2: Direct Command

```bash
docker compose down
```

---

## Additional Notes

- Ensure Docker is running before starting any service
- All required ports must be available on your system
- For more information about RAGFlow, consult the [official documentation](https://ragflow.io/docs)

---


## Contribution

If you encounter any problems or have suggestions for improvements:

1. Open an [issue](https://github.com/MikelBarajas38/AVRI-Back/issues)
2. Submit a pull request with your proposed changes

For more details on contributing, please review our [contribution guidelines](CONTRIBUTING.md).

---
