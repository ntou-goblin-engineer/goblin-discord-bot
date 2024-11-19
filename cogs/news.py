import json
import asyncio
import datetime
import discord
import discord.ext.commands
import discord.ext.tasks
import requests
from bs4 import BeautifulSoup

class NewsCog(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    def beautiful_soup(self, url: str) -> BeautifulSoup:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, "html.parser")
        return soup

    @discord.app_commands.command(name="news_latest", description="最新消息")
    async def news_latest(self, interaction: discord.Interaction):
        link = "https://cse.ntou.edu.tw/p/403-1063-1034-1.php?Lang=zh-tw"
        response = self.beautiful_soup(link)
        news = response.find("div", class_ = "row listBS")
        title = news.find("a")["title"]
        date = news.find("i", class_ = "mdate after").get_text()
        link = news.find("a")["href"]
        response = self.beautiful_soup(link)
        content = response.find("div", class_ = "mpgdetail").get_text()
        embed = discord.Embed(
            title=title,
            url=link,
            colour=discord.Colour.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name=":calendar_spiral: 日期", value=date, inline=False)
        embed.add_field(name=":placard: 內容", value=content.strip(), inline=False)
        embed.set_footer(text="國立海洋大學資訊工程學系消息")
        await interaction.response.send_message(embed=embed)

class NewsTask(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.channel_id = "1308463119210643476"
        self.news_update.start()

    tz = datetime.timezone(datetime.timedelta(hours=8))
    everyday_time = datetime.time(hour=8, minute=0, tzinfo=tz)

    def beautiful_soup(self, url: str) -> BeautifulSoup:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, "html.parser")
        return soup

    @discord.ext.tasks.loop(minutes=1)
    async def news_update(self):
        with open("news.json", "r", encoding="utf8") as file:
            news_data = json.load(file)
        s = set(news_data)
        link = "https://cse.ntou.edu.tw/p/403-1063-1034-1.php?Lang=zh-tw"
        response = self.beautiful_soup(link)
        news_list = response.find_all("div", class_ = "row listBS")
        news_list.reverse()
        for news in news_list:
            title = news.find("a")["title"]
            date = news.find("i", class_ = "mdate after").get_text()
            link = news.find("a")["href"]
            if title not in s:
                s.add(title)
                response = self.beautiful_soup(link)
                content = response.find("div", class_ = "mpgdetail").get_text()
                if len(content) > 1000:
                    content = content[:1000] + "......"
                embed = discord.Embed(
                    title=title,
                    url=link,
                    colour=discord.Colour.blue(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name=":calendar_spiral: 日期", value=date, inline=False)
                embed.add_field(name=":placard: 內容", value=content.strip(), inline=False)
                embed.set_footer(text="國立海洋大學資訊工程學系消息")
                await self.bot.get_channel(int(self.channel_id)).send(embed=embed)
            await asyncio.sleep(3)
        with open("news.json", "w", encoding="utf8") as file:
            json.dump(list(s), file, ensure_ascii=False, indent=4)

    @news_update.before_loop
    async def news_update_before(self):
        await self.bot.wait_until_ready()

async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(NewsCog(bot))
    await bot.add_cog(NewsTask(bot))
