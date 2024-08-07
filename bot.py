import discord
import sqlite3
import os
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Conecta la base de datos SQLite
conn = sqlite3.connect('vip_data.db')
cursor = conn.cursor()

# Crea la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS vip_users (
    id INTEGER PRIMARY KEY,
    tipo_vip TEXT,
    fecha_ingreso TEXT,
    fecha_modificacion TEXT
)
''')
conn.commit()

# Configura el bot de Discord con un prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

# Comando para insertar un nuevo ID con el tipo de VIP
@bot.command(name='ingresar')
async def insertar(ctx, id: int, tipo_vip: str):
    # Validar tipo de VIP
    if tipo_vip.lower() not in ["bronce", "plata", "oro", "platino"]:
        await ctx.send(f"Tipo de VIP inválido: {tipo_vip}. Debe ser 'bronce', 'plata', 'oro' o 'platino'.")
        return

    # Obtener la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Verifica si el ID ya existe
    cursor.execute('SELECT id FROM vip_users WHERE id = ?', (id,))
    if cursor.fetchone() is not None:
        await ctx.send(f"El usuario con ID {id} ya existe.")
        return

    # Inserta el nuevo usuario VIP
    cursor.execute('INSERT INTO vip_users (id, tipo_vip, fecha_ingreso, fecha_modificacion) VALUES (?, ?, ?, ?)', 
                (id, tipo_vip, fecha_actual, fecha_actual))
    conn.commit()
    await ctx.send(f'Nuevo usuario VIP insertado: ID {id} con VIP {tipo_vip}')

# Comando para editar el tipo de VIP de un ID
@bot.command(name='editar')
async def editar(ctx, id: int, nuevo_tipo_vip: str):
    # Validar tipo de VIP
    if nuevo_tipo_vip.lower() not in ["bronce", "plata", "oro", "platino"]:
        await ctx.send(f"Tipo de VIP inválido: {nuevo_tipo_vip}. Debe ser 'bronce', 'plata', 'oro' o 'platino'.")
        return

    # Verifica si el ID existe
    cursor.execute('SELECT id FROM vip_users WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        await ctx.send(f"No se encontró usuario VIP con ID {id}.")
        return

    # Actualiza el tipo de VIP y la fecha de modificacion
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE vip_users SET tipo_vip = ?, fecha_modificacion = ? WHERE id = ?', 
                (nuevo_tipo_vip, fecha_actual, id))
    conn.commit()
    await ctx.send(f'Tipo de VIP actualizado para ID {id} a {nuevo_tipo_vip}')

# Comando para borrar un ID de la base de datos
@bot.command(name='borrar')
async def borrar(ctx, id: int):
    # Verifica si el ID existe
    cursor.execute('SELECT id FROM vip_users WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        await ctx.send(f"No se encontró usuario VIP con ID {id}.")
        return

    # Borra el usuario VIP
    cursor.execute('DELETE FROM vip_users WHERE id = ?', (id,))
    conn.commit()
    await ctx.send(f'Usuario VIP con ID {id} borrado')

# Comando para listar todos los IDs con sus tipos de VIP
@bot.command(name='lista')
async def listar(ctx):
    cursor.execute('SELECT * FROM vip_users')
    rows = cursor.fetchall()
    if rows:
        message = '**Lista de usuarios VIP:**\n'
        for row in rows:
            message += f'ID: {row[0]}, Tipo de VIP: {row[1]}, Ingreso: {row[2]}, Modificado: {row[3]}\n'
        await ctx.send(message)
    else:
        await ctx.send('No hay usuarios VIP en la base de datos.')

# Comando para obtener el tipo de VIP de un ID específico usando el prefix "!"
@bot.event
async def on_message(message):
    # Ignorar mensajes del bot
    if message.author == bot.user:
        return

    # Verifica si el mensaje comienza con "!" seguido de un numero/ID
    if message.content.startswith('!') and message.content[1:].isdigit():
        id = int(message.content[1:])
        
        # Consulta el ID en la base de datos
        cursor.execute('SELECT tipo_vip, fecha_ingreso, fecha_modificacion FROM vip_users WHERE id = ?', (id,))
        row = cursor.fetchone()
        
        if row:
            await message.channel.send(f'ID {id} tiene tipo de VIP: {row[0]}, Ingreso: {row[1]}, Modificado: {row[2]}')
        else:
            await message.channel.send(f'No se encontró usuario VIP con ID {id}')
    
    # Procesar otros comandos
    await bot.process_commands(message)

# Ejecuta el bot
bot.run(TOKEN)