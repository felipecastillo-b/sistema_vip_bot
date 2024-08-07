# Sistema Vip Bot GTA RP

Este es un bot de Discord realizado en Python que utiliza una base de datos SQLite para gestionar datos de usuarios VIP para un taller mecanico en GTA RP. El bot ofrece comandos para añadir, editar, borrar y consultar usuarios con diferentes niveles de VIP.
La finalidad de este bot es poder facilitar la verificacion y gestion del VIP de clientes del taller mecanico.
## Funcionalidades
- !lista : Muestra la lista de todos los ID con su respectivo VIP, fecha de ingreso y modificacion
- !ingresar : Ingresa un ID con su respectivo VIP (!ingresar 4771 platino)
- !editar : Edita el VIP de un ID en especifico (!editar 4770 oro)
- !borrar : Borra los datos del ID totalmente (!borrar 4920)
- !id : Muestra los datos del ID en especifico (!4771)

## Requisitos y Tecnologias

- Python 3.10 o superior

## Instalación

Sigue estos pasos para configurar y ejecutar el bot en tu entorno local.

### 1. Clonar el Repositorio

Clona este repositorio a tu máquina local:

```bash
git clone https://github.com/felipecastillo-b/sistema_vip_bot
cd sistema_vip_bot
```

### 2. Crear un Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar el Token del Bot

```bash
crear un .env en la raiz del proyecto
TOKEN=your_discord_bot_token
```

### 5. Ejecutar el Bot

```bash
python bot.py
```

## Contribuciones al Codigo / Proyecto

Si deseas contribuir a este proyecto, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tus cambios.
3. Realiza tus modificaciones.
4. Envía un pull request con una descripción clara de tus cambios.

## Contribuciones y Apoyo

Si encuentras útil este proyecto y deseas apoyarlo, puedes hacerlo de varias maneras:

- **Donaciones:** Si te gustaría apoyar el desarrollo continuo y la mejora de este proyecto, puedes hacer una donación en [Buy Me a Coffee](https://buymeacoffee.com/felipecastillo). Tu contribución ayudará a cubrir los costos de desarrollo y mantener el proyecto actualizado.
- **Comparte el Proyecto:** Ayuda a difundir el proyecto compartiéndolo con otros. Cuantos más usuarios lo conozcan, más útil será para la comunidad.
- **Feedback:** Si tienes comentarios o sugerencias, no dudes en contactarme. Siempre estoy buscando maneras de mejorar el proyecto.

Cada aporte es muy apreciado y contribuye directamente a la calidad y sostenibilidad del proyecto. ¡Gracias por tu apoyo!
