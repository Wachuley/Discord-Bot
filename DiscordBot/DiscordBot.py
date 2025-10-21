import discord
from discord.ext import commands
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

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    mensaje = message.content.lower().strip()
    
    # Respuestas a saludos
    if mensaje in ['hola', 'holi', 'hello', 'hi', 'hey']:
        saludos = [
            "¡Hola!",
            "¡Hey! ¿Cómo estás?",
            "¡Holi!",
            "¡Saludos!",
            "¡Hola! ¿En qué puedo ayudarte?"
        ]
        await message.channel.send(random.choice(saludos))
    
    await bot.process_commands(message)


bot.run(TOKEN)