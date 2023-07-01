import discord
from discord.ext import tasks
from mcstatus import JavaServer
import asyncio

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_message = None
    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        self.mc_status_update.start()  # start the task here

    @tasks.loop(seconds=7)  # adjust the time interval as needed
    async def mc_status_update(self):
        channel = self.get_channel(1121442282353213560)  # replace with your channel ID
        server = JavaServer.lookup("grogl.zapto.org:25566")  # replace with your server IP and port
        status = server.status()

        player_list = ', '.join([player.name for player in status.players.sample]) if status.players.sample else 'No players online'

        embed = discord.Embed(
            title="Minecraft Server Status",
            description="**grogl.zapto.org:25566**",
            color=discord.Color.green()
        )
        embed.add_field(name="Players Online",value=f"{status.players.online}/{status.players.max}")
        embed.add_field(name="Latency",value=f"{status.latency:.2f}ms")
        embed.add_field(name="Version",value=status.version.name,inline="true")
        embed.add_field(name="Online Players", value=player_list)
        embed.set_footer(text="grogl.zapto.org:25566")

        if self.last_message:
            try:
                await self.last_message.edit(embed=embed)
            except discord.NotFound:
                self.last_message = await channel.send(embed=embed)
        else:
            self.last_message = await channel.send(embed=embed)
        await asyncio.sleep(7)

# Create an instance of the bot
intents = discord.Intents.default()
intents.message_content = True
client = MyBot(intents=intents)

# Run the bot
client.run('MTEyMTQxOTE0NzczODM1NzgwMQ.GLEMNm.UquzV0K9qClqRFFMSQmFsAXaQS01oIgyeFhYys')  # replace with your bot token
