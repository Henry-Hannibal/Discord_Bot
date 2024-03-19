import os
import discord
import responses
from discord import Intents
from discord.ext import commands
import pathlib

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
        
        
def run_discord_bot():
    TOKEN = os.getenv("MarioBotToken")
    
    
    client = discord.Client(intents=discord.Intents(message_content=True, messages=True, guilds=True))
    
    
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
    
    
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        
        
        
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        print(f"{username} said: '{user_message}' ({channel})")
        
        
        if user_message[0:2] == '!l':
            print(user_message)
            try:
                response = responses.handle_response(user_message)
            
                response = str(response)
                if(response[0:4]=="OUT:"): # This is for the error messages in the "!l change" path and for the help message
                    await message.channel.send(response[4:])
                    response = False
                        
                
                if(response):
                    j = pathlib.Path("Leaderboard.txt")
                    f = discord.File(j) #, filename="test.txt"
                    
                    embed = discord.Embed(title="Leaderboard")
                    embed.set_image(url=f"attachment://{f}")
                    await message.channel.send(embed=embed, file=f)
                    
                    if(type(response)==str and response!="True"):
                        await message.channel.send(response)
            except Exception as e:
                print(e)
        
    
    
        
    client.run(TOKEN)
    
    
    
    
