import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Cargar el archivo .env con el token del bot
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

print(f"Token cargado: {TOKEN}")
