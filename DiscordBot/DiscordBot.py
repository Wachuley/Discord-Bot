import discord
from discord import channel
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} está conectado!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="tus mensajes"))
    try:
        synced = await bot.tree.sync()
        print(f"Se han sincronizado {len(synced)} comandos slash.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    mensaje = message.content.lower().strip()
    
    # Respuestas a saludos
    if mensaje in ['hola', 'holi', 'hello', 'hi', 'hey']:
        saludos = [
            "¡Hola!",
            "¡Heyyy!",
            "¡Holi!",
            "¡Saludos!",
            "¡Holaaaa!"
        ]
        await message.channel.send(random.choice(saludos))
    
    await bot.process_commands(message)

#Crear el comando para reproducir la canción
#La query es el estado de ánimo okei

@bot.tree.command(name="play", description="Reproduce una canción según tu estado de ánimo :)")
@app_commands.describe(query="Search query")
async def play(interaction: discord.Interaction, query:str):
    await interaction.response.defer()

    #Para verificar que el usuario esté en un canal de voz
    voice_channel = interaction.user.voice.channel
    if voice_channel is None:
        await interaction.followup.send("Debes estar en un canal de voz :p")
        return

    voice_client = interaction.guild.voice_client

    #Conectar al bot al canal de voz
    if voice_client is None:
        voice_client = await voice_channel.connect()
    #Asegurarnos de que esté en el mismo canal de voz que el usuario
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    #Aquí debería ir todo para reproducir la canción okei
    await interaction.followup.send(f"Buscando canciones para cuando te sientes {query}")



bot.run(TOKEN)