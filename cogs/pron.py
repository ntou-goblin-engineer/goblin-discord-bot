import json
import asyncio
import datetime
import discord
import discord.ext.commands
import discord.ext.tasks
from bs4 import BeautifulSoup
from selenium import webdriver

class MissAVCog(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="missav_today_hot", description="MissAV 今日熱門排行")
    async def missav_today_hot(self, interaction: discord.Interaction):
        await interaction.response.defer()
        driver = webdriver.Chrome()
        url = "https://missav.com/today-hot"
        driver.get(url)
        await asyncio.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        embed = discord.Embed(
            title="<:MissAV:1308487637975437373> MissAV 今日熱門排行",
            url=url,
            colour=discord.Colour.pink(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Miss AV 資訊系統")
        rank = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", "nine", ":keycap_ten:"]
        av_list = soup.find_all("div", class_="thumbnail group")
        for i in range(10):
            img = av_list[i].find("img", class_="w-full")["data-src"]
            a_tag = av_list[i].find("a", class_="text-secondary group-hover:text-primary")
            link = f"https://missav.com/{a_tag['alt']}"
            number, title = a_tag.get_text().strip().split(" ", 1)
            embed.add_field(name=f"{rank[i]} {number} {title}", value=f"{link}", inline=False)
        driver.quit()
        await interaction.followup.send(embed=embed)

async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(MissAVCog(bot))

