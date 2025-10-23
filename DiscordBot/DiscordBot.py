import discord
from discord import channel
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

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



#-----------------------------------------------------------



@bot.tree.command(name="mood", description="Te recomiendo canciones según tu estado de ánimo 🎧")
@app_commands.describe(feeling="Escribe cómo te sientes (feliz, triste, relajado, etc.)")
async def mood(interaction: discord.Interaction, feeling: str):
    await interaction.response.defer()

    try:
        # Mapeo más inteligente: género + año + características
        mood_config = {
            "feliz": {
                "genres": ["pop", "dance", "disco"],
                "year": "2010-2024",
                "keywords": "upbeat"
            },
            "triste": {
                "genres": ["acoustic", "sad", "piano"],
                "year": "2000-2024", 
                "keywords": "emotional"
            },
            "relajado": {
                "genres": ["chill", "ambient", "jazz"],
                "year": "1990-2024",
                "keywords": "calm"
            },
            "enojado": {
                "genres": ["rock", "metal", "punk"],
                "year": "1990-2024",
                "keywords": "intense"
            },
            "enamorado": {
                "genres": ["r-n-b", "soul", "pop"],
                "year": "2000-2024",
                "keywords": "romantic"
            },
            "depresion extrema": {
            "genres": ["sad", "emo", "acoustic", "piano", "indie", "singer-songwriter"],
            "year": "2000-2024",
            "keywords": "heartbreak depressive melancholic"
            }
        }
        
        feeling_lower = feeling.lower()
        
        if feeling_lower in mood_config:
            config = mood_config[feeling_lower]
            selected_genre = random.choice(config["genres"])
            year_range = config["year"]
            keyword = config["keywords"]
            
            search_query = f"genre:{selected_genre} year:{year_range} {keyword}"
        else:
            # Búsqueda genérica
            selected_genre = "pop"
            search_query = f"genre:{selected_genre}"

        print(f"🎯 Buscando: '{search_query}'")
        
        # Buscar playlists primero
        results = sp.search(q=search_query, type='playlist', limit=5)
        playlists = results['playlists']['items']
        
        all_tracks = []
        
        if playlists:
            # Tomar hasta 3 playlists y mezclar sus canciones
            for playlist in playlists[:3]:
                try:
                    playlist_tracks = sp.playlist_tracks(playlist['id'], limit=15)
                    tracks = [item['track'] for item in playlist_tracks['items'] if item['track']]
                    all_tracks.extend(tracks)
                except:
                    continue
        
        # Si no hay suficientes canciones, buscar tracks directamente
        if len(all_tracks) < 5:
            track_results = sp.search(q=f"genre:{selected_genre}", type='track', limit=20)
            all_tracks.extend(track_results['tracks']['items'])
        
        # Seleccionar aleatoriamente
        if all_tracks:
            selected_tracks = random.sample(all_tracks, min(5, len(all_tracks)))
            
            respuesta = f"🎵 **Recomendaciones para '{feeling}'**:\n\n"
            for i, track in enumerate(selected_tracks, 1):
                nombre = track['name']
                artista = track['artists'][0]['name']
                url = track['external_urls']['spotify']
                respuesta += f"**{i}. {nombre}** — {artista}\n🔗 {url}\n\n"
            
            await interaction.followup.send(respuesta)
        else:
            await interaction.followup.send(f"😅 No encontré canciones para '{feeling}'.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await interaction.followup.send(f"⚠️ Error: {e}")


bot.run(TOKEN)