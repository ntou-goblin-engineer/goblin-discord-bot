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
        self.rank = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]

    class TodayHotView(discord.ui.View):
        def __init__(self, rank, av_data, interaction: discord.Interaction, timeout=180):
            super().__init__(timeout=timeout)
            self.rank = rank
            self.av_data = av_data
            self.interaction = interaction
            for i in range(10):
                button = discord.ui.Button(
                    label=str(i + 1).zfill(2),
                    style=discord.ButtonStyle.blurple,
                    custom_id=str(i)
                )
                button.callback = self.callback
                self.add_item(button)

        async def on_timeout(self):
            try:
                embed = discord.Embed(
                    title="進入聖人模式",
                    colour=discord.Colour.yellow(),
                    timestamp=datetime.datetime.now()
                )
                embed.set_image(url="https://www.chinasona.org/Thiaoouba/jesus.jpg")
                embed.set_footer(text="NTOU Goblin Engineer 製作")
                await self.interaction.edit_original_response(embed=embed, view=None)
            except Exception as err:
                print(err)

        async def callback(self, interaction: discord.Interaction):
            index = int(interaction.data["custom_id"])
            embed = discord.Embed(
                title=f"{self.rank[index]} 【{self.av_data[index]['number']}】{self.av_data[index]['length']}",
                description = self.av_data[index]["title"],
                url = self.av_data[index]["link"],
                colour=discord.Colour.pink(),
                timestamp=datetime.datetime.now()
            )
            embed.set_image(url=self.av_data[index]["image"])
            embed.set_footer(text="NTOU Goblin Engineer 製作")
            await interaction.response.edit_message(embed=embed)

    @discord.app_commands.command(name="missav_rank", description="MissAV 排行")
    @discord.app_commands.describe(option = "選擇類別")
    @discord.app_commands.choices(
        option = [
            discord.app_commands.Choice(name="最近更新", value="new"),
            discord.app_commands.Choice(name="今日熱門", value="today-hot"),
            discord.app_commands.Choice(name="本週熱門", value="weekly-hot"),
            discord.app_commands.Choice(name="本月熱門", value="monthly-hot")
        ]
    )
    async def missav_rank(self, interaction: discord.Interaction, option: discord.app_commands.Choice[str]):
        await interaction.response.defer()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        url = f"https://missav.com/{option.value}"
        driver.get(url)
        await asyncio.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        av_list = soup.find_all("div", class_="thumbnail group")
        av_data = []
        embed = discord.Embed(
            title="<:MissAV:1308487637975437373> MissAV 今日熱門排行",
            url=url,
            colour=discord.Colour.pink(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="NTOU Goblin Engineer 製作")
        for i in range(10):
            try:
                image = av_list[i].find("img", class_="w-full")["data-src"]
                video = av_list[i].find("video", class_="preview hidden")["data-src"]
                length = av_list[i].find("span", class_="absolute bottom-1 right-1 rounded-lg px-2 py-1 text-xs text-nord5 bg-gray-800 bg-opacity-75").get_text().strip()
                a_tag = av_list[i].find("a", class_="text-secondary group-hover:text-primary")
                link = f"https://missav.com/{a_tag['alt']}"
                number, title = a_tag.get_text().strip().split(" ", 1)
                embed.add_field(name=f"{self.rank[i]} 【{number}】{length}", value=f"[{title}]({link})", inline=False)
                av_data.append({"number": number, "title": title, "length": length, "link": link, "image": image, "video": video})
            except Exception as err:
                pass
        driver.quit()
        view = self.TodayHotView(rank=self.rank, av_data=av_data, interaction=interaction)
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(MissAVCog(bot))

