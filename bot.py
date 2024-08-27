import discord
import sqlite3
import os
from datetime import datetime
from discord.ext import commands, tasks
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
    mecanico INTEGER DEFAULT 1,
    estetico INTEGER DEFAULT 1,
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
    reset_mecanico_estetico.start() # Inicia la tarea programada al iniciar el bot

# Comando para insertar un nuevo ID con el tipo de VIP opcional
@bot.command(name='ingresar')
async def insertar(ctx, id: int, tipo_vip: str = ''):
    # Validar tipo de VIP | se quito porque ya no era necesario
    if tipo_vip.lower() not in ["rex", "obsidian", "ems", "otro"]:
        await ctx.send(f"Tipo de VIP inválido: {tipo_vip}. Debe ser 'rex', 'obsidian', 'ems' o 'otro'.")
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
    if nuevo_tipo_vip.lower() not in ["rex", "obsidian", "ems", "otro"]:
        await ctx.send(f"Tipo de VIP inválido: {nuevo_tipo_vip}. Debe ser 'rex', 'obsidian', 'ems' o 'otro'.")
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
            message += f'ID: {row[0]}, Tipo de VIP: {row[1]}, Mecanico: {row[2]}, Estetico {row[3]}, Ingreso: {row[4]}, Modificado: {row[5]}\n'
        await ctx.send(message)
    else:
        await ctx.send('No hay usuarios VIP en la base de datos.')



# Comando para obtener el tipo de VIP de un ID específico usando el prefix "!"
@bot.event
async def on_message(message):
    # Ignorar mensajes del bot
    if message.author == bot.user:
        return

    #  Verifica si el mensaje comienza con "!" seguido de un numero/ID
    if message.content.startswith('!'):
        parts = message.content[1:].split()

        if parts[0].isdigit():
            id = int(parts[0])
            
            # Si tiene dos partes y la segunda es 'mecanico' o 'estetico'
            if len(parts) > 1 and parts[1].lower() in ["mecanico", "estetico"]:
                tipo = parts[1].lower()

                # Consulta el ID en la base de datos
                cursor.execute(f'SELECT {tipo} FROM vip_users WHERE id = ?', (id,))
                row = cursor.fetchone()

                if row is not None:
                    # Setea el valor a 0 y actualiza la fecha de modificación
                    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(f'UPDATE vip_users SET {tipo} = 0, fecha_modificacion = ? WHERE id = ?', 
                                (fecha_actual, id))
                    conn.commit()
                    await message.channel.send(f'Tuneo {tipo.capitalize()} actualizado a 0 para ID {id}')
                else:
                    await message.channel.send(f'No se encontró usuario VIP con ID {id}')
            else:
                # Si no se menciona 'mecanico' o 'estetico', muestra el tipo de VIP
                cursor.execute('SELECT mecanico, estetico FROM vip_users WHERE id = ?', (id,))
                row = cursor.fetchone()
                
                if row:
                    await message.channel.send(f'ID {id} tiene Descuento Mecanico: {row[0]}, Descuento Estetico: {row[1]}')
                else:
                    await message.channel.send(f'No se encontró usuario VIP con ID {id}')
    
    # Procesar otros comandos
    await bot.process_commands(message)

# Tarea programada para resetear mecanico y estetico a 1 cada Lunes a las 20:00 (si afecta el rendimiento cambiar a solo Lunes)
@tasks.loop(minutes=10) # Verifica cada 10 minutos (ver rendimiento)
async def reset_mecanico_estetico():
    # Obtener la fecha actual del sistema
    now = datetime.now()

    # Verifica si es Lunes y las 20:00 (Tormenta en HispanoRP)
    if now.weekday() == 0 and now.hour == 20:
        cursor.execute('UPDATE vip_users SET mecanico = 1, estetico = 1')
        conn.commit()
        print('Valores de mecanico y estetico reseteados a 1 para todos los usuarios')

# Ejecuta el bot
bot.run(TOKEN)