import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DoomSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.game_state = None
        self.current_message = None
        self.ascii_frame = None

class DoomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        super().__init__(command_prefix='!', intents=intents)
        self.active_sessions = {}

    async def setup_hook(self):
        print(f'{self.user} has connected to Discord!')

    async def start_game(self, ctx):
        """Start a new DOOM game session"""
        if ctx.author.id in self.active_sessions:
            await ctx.send("You already have an active game session!")
            return
        
        session = DoomSession(ctx.author.id)
        self.active_sessions[ctx.author.id] = session
        # Initialize game display will be implemented later
        await ctx.send("Starting DOOM... Get ready!")

bot = DoomBot()

@bot.command(name='doom')
async def doom(ctx):
    """Start a new game of DOOM"""
    await bot.start_game(ctx)

def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in .env file")
    bot.run(token)

if __name__ == '__main__':
    main()
