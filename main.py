import os
import asyncio
import dotenv
import discord
import discord.ext.commands

dotenv.load_dotenv()
intents = discord.Intents.all()
bot = discord.ext.commands.Bot(command_prefix="&", intents=intents)

@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"{bot.user} is online.")
    print(f"Synced {len(slash)} slash command.")

async def main():
    async with bot:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
