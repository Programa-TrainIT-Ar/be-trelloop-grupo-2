# INSTALACIÓN DEL PROYECTO PRUEBA

### 0 A una carpeta ya inicializada, añadir el origin remoto

`git remote add origin https://github.com/Programa-TrainIT-Ar/be-trelloop-grupo-2`

### 0.1 Hacer un git pull a la rama local main

`git pull origin main`

### 1 Crear un entorno virtual en el root

`python -m venv venv`

### 2 Activar el entorno virtual

`source venv/Scripts/activate`

### 3 Instalar requirements.txt

`pip install -r requirements.txt`

### 4 Crear la varialble de entorno desde el root para flask migrations (git bash)

`export FLASK_APP=app.main:app`

### 5 Crear nuevamente la base de datos y conectarla en el .env

### 6 Definir las variables requeridas en un .env. Las variables necesarias estan en .env.example

### 7 Traer las migraciones

`flask db upgrade`

### 8 Inicializar la aplicacion flask.

`python -m app.main`
