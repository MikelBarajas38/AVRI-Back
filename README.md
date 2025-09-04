<div align="center">
  <a href="#">
    <picture>
      <source srcset="assets/img/iconbot-dark.png" media="(prefers-color-scheme: dark)">
      <source srcset="assets/img/iconbot-light.png" media="(prefers-color-scheme: light)">
      <img src="assets/img/iconbot-light.png" width="520" alt="AVRI logo">
    </picture>
  </a>
</div>


# AVRI-Back

API para el Asistente Virtual del Repositorio Institucional

## Pre-requisitos
1- Hacer git clone a este repositorio con:
  $ git clone https://github.com/MikelBarajas38/AVRI-Back.git
2- Una vez clonado el repositorio es necesario navegar hasta el (Se puede hacer usando los comandos "cd")
3- Inicializar docker (independientemente si es Linux, Windows, etc) el servicio debe iniciar
  3.1- Inicializar RAGFLOW primeramente, si requiere de más infromación por favor navegue a la carpeta donde tenga RAGFLOW instalado y ejecute los siguientes comandos:
    $ docker compose -f docker/docker-compose.yml up -d
    $ docker logs -f ragflow-server
    Si todo se ejecutó correctamente debería de poder ver "RAGFLOW" escrito en arte ascci y la oráción "TASK EXECUTOR"
    <img width="1723" height="337" alt="image" src="https://github.com/user-attachments/assets/284a1b31-379a-4779-853d-7cedecfde258" />

4- Una vez se este en la carpeta de "AVRI-BACK" se deberá ejecutar el siguiente comando:
  $ docker compose -f docker-compose.yml -f docker-compose.ragflow.yml up
    El comando nos servirá para inicializar el contenedor 
5- Verificar los logs, si todo se ah ejecutado correctamente se recuerda que se deben de ver los logs similares a estos:
<img width="1747" height="321" alt="image" src="https://github.com/user-attachments/assets/93ffcfc4-c321-4117-8f88-5e010f870925" />
