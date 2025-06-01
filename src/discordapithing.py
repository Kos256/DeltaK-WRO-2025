import discord

class DiscordRemote(discord.Client):
    def __init__(self, *, token):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.token = token

        # Register slash commands inside __init__
        self.tree.add_command(discord.app_commands.Command(
            name="ping",
            description="Expects a pong",
            callback=self._ping,
        ))

    def runBot(self): self.run(self.token)

    async def _ping(self, interaction: discord.Interaction, value: float):
        await interaction.response.send_message(f"pong (value: {value})", ephemeral=True)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(name="Running on the DeltaK bot currently")
        )
        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} commands.')
        except Exception as e:
            print(f'Error syncing commands: {e}')

bot = DiscordRemote(token="MTM3NzU0NjM0ODM4MzE3NDY3Ng.GWy7Qp.tuqDIULSUyN1Vzp9U0CnxtKxCYnnIP3RVtiW1s")
bot.runBot()