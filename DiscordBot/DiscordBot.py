import discord
from discord import channel
from discord.ext import commands
from discord import app_commands
import os
from discord.ui import View, Button
import asyncio
from dotenv import load_dotenv
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

#Variables pa las stats
mood_usage = {} #Este diccionario guarda de que los estados de ánimo y cuantas veces se usaron
total_commands = 0

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

@bot.tree.command(name="help", description="❓ Muestra información sobre cómo usar el bot")
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer()
    total_commands += 1
    
    try:
        embed = discord.Embed(
            title="Guía del Bot de Música por Estados de Ánimo",
            description="Descubre música según tu estado de ánimo :D",
            color=0x7a00bb
        )
        
        # Comandos disponibles
        embed.add_field(
            name="Comandos",
            value=(
                "`/mood [estado]` - Recomendaciones musicales personalizadas\n"
                "`/stats` - Ver estadísticas de uso del bot\n"
                "`/help` - Guía de ayuda\n"
            ),
            inline=False
        )
        
        # Estados de ánimo yasss
        embed.add_field(
            name="Estados de Ánimo Disponibles",
            value=(
                "• **feliz**\n"
                "• **triste**\n"
                "• **relajado**\n"
                "• **enojado**\n"
                "• **enamorado**\n"
                "• **depresion extrema >:)**\n"
            ),
            inline=False
        )
        
        # Cómo usar (super difici)
        embed.add_field(
            name="Cómo Usar",
            value=(
                "1. Usa `/mood` seguido de tu estado de ánimo\n"
                "2. El bot te mostrará 5 canciones personalizadas\n"
                "3. Cada canción viene con información completa\n"
                "4. Puedes hacer clic en el título para abrir en Spotify"
            ),
            inline=False
        )
        
        # Características
        embed.add_field(
            name="Características",
            value=(
                "• Recomendaciones basadas en tu estado emocional\n"
                "• Información de cada canción\n"
                "• Enlaces directos a Spotify\n"
                "• Portadas de álbum\n"
                "• Estadísticas de uso\n"
            ),
            inline=False
        )
        
        embed.set_footer(text="A todos les gusta la música yei")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Error en help: {e}")
        await interaction.followup.send("⚠️ Hubo un error al mostrar el comando de ayuda")



#-----------------------------------------------------------



@bot.tree.command(name="mood", description="Te recomiendo canciones según tu estado de ánimo 🎧")
@app_commands.describe(feeling="Escribe cómo te sientes (feliz, triste, relajado, etc.)")
async def mood(interaction: discord.Interaction, feeling: str):
    await interaction.response.defer()

    # aqui se actualizan las stats
    global total_commands, mood_usage
    total_commands += 1
    mood_usage[feeling.lower()] = mood_usage.get(feeling.lower(), 0) + 1

    try:
        # Mapeo con colores, se ve coqueto
        mood_config = {
            "feliz": {
                "genres": ["pop", "dance", "disco"],
                "year": "2010-2024",
                "keywords": "upbeat",
                "color": 0xFCEF00,
                "emoji": "😄"
            },
            "triste": {
                "genres": ["acoustic", "sad", "piano"],
                "year": "2000-2024", 
                "keywords": "emotional",
                "color": 0x3498DB, 
                "emoji": "😢"
            },
            "relajado": {
                "genres": ["chill", "ambient", "jazz"],
                "year": "1990-2024",
                "keywords": "calm",
                "color": 0x2ECC71, 
                "emoji": "😌"
            },
            "enojado": {
                "genres": ["rock", "metal", "punk"],
                "year": "1990-2024",
                "keywords": "intense",
                "color": 0xE74C3C, 
                "emoji": "😠"
            },
            "enamorado": {
                "genres": ["r-n-b", "soul", "pop"],
                "year": "2000-2024",
                "keywords": "romantic",
                "color": 0xE84393, 
                "emoji": "🥰"
            },
            "depresion extrema": {
                "genres": ["sad", "emo", "acoustic", "piano", "indie", "singer-songwriter"],
                "year": "2000-2024",
                "keywords": "heartbreak depressive melancholic",
                "color": 0x6C5CE7,
                "emoji": "💔"
            }
        }
        
        feeling_lower = feeling.lower()
        
        if feeling_lower in mood_config:
            config = mood_config[feeling_lower]
            selected_genre = random.choice(config["genres"])
            year_range = config["year"]
            keyword = config["keywords"]
            embed_color = config["color"]
            mood_emoji = config["emoji"]
            
            search_query = f"genre:{selected_genre} year:{year_range} {keyword}"
        else:
            # Configuración por defecto
            selected_genre = "pop"
            search_query = f"genre:{selected_genre}"
            embed_color = 0x1DB954
            mood_emoji = "🎵"

        print(f"🎯 Buscando: '{search_query}'")
        
        # Buscar playlists primero
        results = sp.search(q=search_query, type='playlist', limit=5)
        playlists = results['playlists']['items']
        
        all_tracks = []
        
        if playlists:
            for playlist in playlists[:3]:
                try:
                    playlist_tracks = sp.playlist_tracks(playlist['id'], limit=15)
                    tracks = [item['track'] for item in playlist_tracks['items'] if item['track']]
                    all_tracks.extend(tracks)
                except:
                    continue
        
        if len(all_tracks) < 5:
            track_results = sp.search(q=f"genre:{selected_genre}", type='track', limit=20)
            all_tracks.extend(track_results['tracks']['items'])
        
        if all_tracks:
            selected_tracks = random.sample(all_tracks, min(5, len(all_tracks)))
            
            # Mensaje principal
            main_message = await interaction.followup.send(
                f"{mood_emoji} *Recomendaciones para '{feeling}'*\n"
            )
            
            #Embeds individuales
            for i, track in enumerate(selected_tracks, 1):
                # Crear embed con color del estado de ánimo
                embed = discord.Embed(
                    title=f"🎵 {i}. {track['name']}",
                    description=f"*Artista:* {track['artists'][0]['name']}",
                    color=embed_color,
                    url=track['external_urls']['spotify']
                )
                
                # Album
                embed.add_field(
                    name="📀 Álbum",
                    value=track['album']['name'],
                    inline=True
                )
                
                # Duración
                duration_ms = track['duration_ms']
                duration_min = f"{(duration_ms // 60000):02d}:{(duration_ms % 60000) // 1000:02d}"
                embed.add_field(
                    name="Duración",
                    value=duration_min,
                    inline=True
                )
                
                # Imagen del álbum
                if track['album']['images']:
                    embed.set_thumbnail(url=track['album']['images'][0]['url'])
                
                # Informacion totalmente necesaria 
                embed.set_footer(
                    text=f"{mood_emoji} Estado: {feeling} • " +
                         f"💿 {selected_genre.title()}"
                )
                
                await interaction.followup.send(embed=embed)
                await asyncio.sleep(0.3)
                
        else:
            await interaction.followup.send(f" No encontré canciones para '{feeling}'.")
        
    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send(f"Error: {e}")




#-----------------------------------------------------------

@bot.tree.command(name="stats", description="Muestra estadísticas de uso del bot")
async def stats(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        total_moods = sum(mood_usage.values())
        moods_ordered = sorted(mood_usage.items(), key=lambda x: x[1], reverse=True) #convierte en duplas y ordena bro ojo
        
        # Crear embed de estadísticas
        embed = discord.Embed(
            title="📊 Estadísticas del Bot de Música",
            description="Datos y preferencias",
            color=0x7a00bb,
            timestamp=discord.utils.utcnow()
        )
        
        #generales
        embed.add_field(
            name="Uso Total",
            value=f"**Comandos ejecutados:** {total_commands}\n"
                  f"**Estados de ánimo pedidos:** {total_moods}",
            inline=False
        )
        
        # Top estados de ánimo claro que si
        if moods_ordered:
            top_moods = ""
            for i, (mood, count) in enumerate(moods_ordered[:5], 1):
                top_moods += f"**{i}. {mood.title()}** - {count} veces\n"
            
            embed.add_field(
                name="Estados de Ánimo Más Populares",
                value=top_moods or "No hay datos aún",
                inline=False
            )
        
        # Datos del servidor porque se ve coqueto
        embed.add_field(
            name="🏠 Este Servidor",
            value=f"**Nombre:** {interaction.guild.name}\n"
                  f"**Miembros:** {interaction.guild.member_count}",
            inline=True
        )
        
        embed.set_footer(text="Send Help")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Error en stats: {e}")
        await interaction.followup.send("Hubo un error al calcular las estadísticas")



bot.run(TOKEN)