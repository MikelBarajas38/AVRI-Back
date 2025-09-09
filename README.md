<div align="center">
  <a href="#">
    <picture>
      <source srcset="assets/img/iconbot-dark.png" media="(prefers-color-scheme: dark)">
      <source srcset="assets/img/iconbot-light.png" media="(prefers-color-scheme: light)">
      <img src="assets/img/iconbot-light.png" width="520" alt="AVRI logo">
    </picture>
  </a>
</div>


# AVRI-Back [![Coverage Status](https://coveralls.io/repos/github/MikelBarajas38/AVRI-Back/badge.svg)](https://coveralls.io/github/MikelBarajas38/AVRI-Back)

## 📋 Tabla de Contenidos

- [Pre-requisitos](#pre-requisitos)
- [Instalación](#instalación)
- [Configuración de RAGFLOW](#configuración-de-ragflow)
- [Ejecución del Proyecto](#ejecución-del-proyecto)
- [Verificación](#verificación)
- [Detener Servicios](#detener-servicios)

---

## 🔧 Pre-requisitos

Antes de comenzar, asegúrate de tener instalado:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) y Docker Compose
- [RAGFLOW](https://ragflow.io/) (configurado previamente)

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/MikelBarajas38/AVRI-Back.git
```

### 2. Navegar al directorio del proyecto

```bash
cd AVRI-Back
```

---

## ⚙️ Configuración de RAGFLOW

> **⚠️ Importante**: RAGFLOW debe estar ejecutándose antes de iniciar AVRI-Back.

### 1. Inicializar RAGFLOW

Navega a la carpeta donde tienes RAGFLOW instalado y ejecuta:

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 2. Verificar logs de RAGFLOW

```bash
docker logs -f ragflow-server
```

### 3. Confirmación exitosa

Si todo se ejecutó correctamente, deberías ver:
- El logo "RAGFLOW" en arte ASCII
- El mensaje "TASK EXECUTOR"

![RAGFLOW Success](https://github.com/user-attachments/assets/284a1b31-379a-4779-853d-7cedecfde258)

---

## 🏃‍♂️ Ejecución del Proyecto

Una vez que RAGFLOW esté ejecutándose, inicia AVRI-Back:

```bash
docker compose -f docker-compose.yml -f docker-compose.ragflow.yml up
```

Este comando inicializará todos los contenedores necesarios.

---

## ✅ Verificación

### Logs exitosos

Si la ejecución es correcta, deberías ver logs similares a estos:

![Success Logs](https://github.com/user-attachments/assets/93ffcfc4-c321-4117-8f88-5e010f870925)

### Estados de los servicios

Puedes verificar el estado de los contenedores con:

```bash
docker ps
```

---

## 🛑 Detener Servicios

### Método 1: Interrupción manual
1. Presiona `Ctrl + C` en la terminal donde están ejecutándose los contenedores
2. Ejecuta el siguiente comando para asegurar que todos los servicios se detengan:

```bash
docker compose down
```

### Método 2: Comando directo
```bash
docker compose down
```

---

## 📝 Notas Adicionales

- Asegúrate de que Docker esté ejecutándose antes de iniciar cualquier servicio
- Los puertos utilizados deben estar disponibles en tu sistema
- Para más información sobre RAGFLOW, consulta su [documentación oficial](https://ragflow.io/docs)

---

## 🤝 Contribución

Si encuentras algún problema o tienes sugerencias de mejora, por favor:

1. Abre un [issue](https://github.com/MikelBarajas38/AVRI-Back/issues)
2. Crea un pull request con tus cambios

---
