import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# Bot setup
bot = commands.Bot(command_prefix="n!")

# Configuration data
config_data = {}

def load_config():
    global config_data
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        # Convert tracked words to lowercase
        config_data["tracked_words"] = [word.lower() for word in config_data["tracked_words"]]
    except FileNotFoundError:
        config_data = {"bot_token": "", "tracked_words": [], "word_counts": {}}

def save_config():
    with open('config.json', 'w') as file:
        json.dump(config_data, file)

# Load the configuration on startup
load_config()

# Event for handling messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    lower_case_message = message.content.lower()
    user = str(message.author)

    for word in config_data["tracked_words"]:
        if word in lower_case_message:
            if user not in config_data["word_counts"].get(word, {}):
                if word not in config_data["word_counts"]:
                    config_data["word_counts"][word] = {}
                config_data["word_counts"][word][user] = 0
            config_data["word_counts"][word][user] += 1

    save_config()
    await bot.process_commands(message)

# Command for displaying the leaderboard
@bot.command(name='leaderboard', help='Displays the word count leaderboard for the specified word.')
async def leaderboard(ctx, word: str):
    word = word.lower()
    if word not in config_data["tracked_words"]:
        await ctx.send(f'Word "{word}" is not being tracked.')
        return
    await display_leaderboard(ctx, word)

# Function to display the leaderboard for a specific word
async def display_leaderboard(ctx, word):
    word_leaderboard = config_data["word_counts"].get(word, {})
    sorted_users = sorted(word_leaderboard.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = f"Word Count Leaderboard for '{word}':\n"
    for user, count in sorted_users:
        leaderboard_text += f"{user}: {count}\n"
    await ctx.send(leaderboard_text)

# Run the bot
bot_token = config_data.get("bot_token")
if bot_token:
    bot.run(bot_token)
else:
    print("Bot token not found in config.json. Please add it and try again.")