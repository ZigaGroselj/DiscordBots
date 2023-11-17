import discord
from discord.ext import commands
import json
import asyncio
import requests

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# Bot setup with intents
bot = commands.Bot(command_prefix="n!", intents=intents)
bot.remove_command('help')

# Configuration data
config_data = {}

def load_config():
    global config_data
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
    except FileNotFoundError:
        config_data = {"bot_token": "", "tracked_words": [], "word_counts": {}}
        save_config()

def save_config():
    with open('config.json', 'w') as file:
        json.dump(config_data, file)

load_config()

# Function to register Slash Command
def register_slash_command(1175105456050540645, 961187820528107520, bot_token):
    url = f"https://discord.com/api/v9/applications/{app_id}/guilds/{guild_id}/commands"
    json = {
        "name": "leaderboard",
        "type": 1,
        "description": "Displays the word count leaderboard",
        "options": [
            {
                "name": "word",
                "description": "The word to display the leaderboard for",
                "type": 3,
                "required": False
            }
        ]
    }
    headers = {
        "Authorization": f"Bot {bot_token}"
    }
    r = requests.post(url, headers=headers, json=json)
    if r.status_code == 201:
        print("Command registered successfully.")
    else:
        print(f"Failed to register command: {r.status_code}\n{r.text}")

# Call the function to register your Slash Command (replace placeholders)
# register_slash_command(app_id='YOUR_APPLICATION_ID', guild_id='YOUR_GUILD_ID', bot_token=config_data.get("bot_token"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    lower_case_message = message.content.lower()
    user = str(message.author)

    for word in config_data["tracked_words"]:
        if word in lower_case_message:
            if word not in config_data["word_counts"]:
                config_data["word_counts"][word] = {}
            config_data["word_counts"][word][user] = config_data["word_counts"][word].get(user, 0) + 1

    save_config()
    await bot.process_commands(message)

@bot.command(name='leaderboard', help='Displays the word count leaderboard for the specified word.')
async def leaderboard(ctx, word: str = 'all'):
    await display_leaderboard(ctx, word)

async def display_leaderboard(ctx, word):
    if word == 'all':
        for word in config_data["tracked_words"]:
            await display_word_leaderboard(ctx, word)
            await asyncio.sleep(1)
    else:
        await display_word_leaderboard(ctx, word)

async def display_word_leaderboard(ctx, word):
    word_leaderboard = config_data["word_counts"].get(word, {})
    if not word_leaderboard:
        await ctx.send(f"No one has used the word '{word}' yet.")
        return
    
    sorted_users = sorted(word_leaderboard.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = f"Word Count Leaderboard for '{word}':\n"
    leaderboard_text += '\n'.join(f"{user}: {count}" for user, count in sorted_users)
    
    await ctx.send(leaderboard_text)

# Handle Slash Command interactions
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.application_command:
        if interaction.data['name'] == 'leaderboard':
            word = interaction.data['options'][0]['value'] if 'options' in interaction.data and interaction.data['options'] else 'all'
            await display_leaderboard(interaction, word)

# Run the bot
bot_token = config_data.get("bot_token")
if isinstance(bot_token, str):
    bot.run(bot_token)
else:
    print("Bot token is not a string. Please check the config.json file.")
