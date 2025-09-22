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


## 📋 Table of Contents
- [Intro](#-avri)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [RAGFLOW Configuration](#️-ragflow-configuration)
- [Running AVRI](#️-running-avri)
- [Verification](#-verification)
- [Stopping AVRI](#-stopping-avri)

---

## 🤖 AVRI

AVRI-Back is the backend system that powers AVRI (Asistente Virtual del Repositorio Institucional), an AI-powered virtual assistant designed to help users navigate and interact with institutional repositories that uses RAGFLOW for document processing and retrieval-augmented generation capabilities.

---

## 🔧 Prerequisites
Before starting, make sure you have installed:
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) and Docker Compose
- [RAGFLOW](https://ragflow.io/) (previously configured)

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/MikelBarajas38/AVRI-Back.git
```

### 2. Navigate to the project directory
```bash
cd AVRI-Back
```

---

## ⚙️ RAGFLOW Configuration
> **⚠️ Important**: RAGFLOW must be running before starting AVRI-Back.

### 1. Initialize RAGFLOW
Navigate to the folder where you have RAGFLOW installed and run:
```bash
docker compose -f docker/docker-compose.yml up -d
```

### 2. Check RAGFLOW logs
```bash
docker logs -f ragflow-server
```

### 3. Successful confirmation
If everything executed correctly, you should see:
- The "RAGFLOW" logo in ASCII art
- The "TASK EXECUTOR" message

![RAGFLOW Success](https://github.com/user-attachments/assets/284a1b31-379a-4779-853d-7cedecfde258)

---

## 🏃‍♂️ Running AVRI
Once RAGFLOW is running, start AVRI-Back:
```bash
docker compose -f docker-compose.yml -f docker-compose.ragflow.yml up
```

This command will initialize all necessary containers.

---

## ✅ Verification

### Successful logs
If the execution is correct, you should see logs similar to these:
![Success Logs](https://github.com/user-attachments/assets/93ffcfc4-c321-4117-8f88-5e010f870925)

### Service status
You can verify the container status with:
```bash
docker ps
```

---

## 🛑 Stopping AVRI

### Method 1: Manual interruption
1. Press `Ctrl + C` in the terminal where the containers are running
2. Execute the following command to ensure all services stop:
```bash
docker compose down
```

### Method 2: Direct command
```bash
docker compose down
```

---

## 📝 Additional Notes
- Make sure Docker is running before starting any service
- The ports used must be available on your system
- For more information about RAGFLOW, consult their [official documentation](https://ragflow.io/docs)

---

## 🤝 Contribution
If you encounter any problems or have improvement suggestions, please:
1. Open an [issue](https://github.com/MikelBarajas38/AVRI-Back/issues)
2. Create a pull request with your changes

---
