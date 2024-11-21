import asyncio
import datetime
import discord
import discord.ext.commands
import discord.ext.tasks
from bs4 import BeautifulSoup
from selenium import webdriver

class MissAV:
    def __init__(self, url: str, embed_title: str, interaction: discord.Interaction):
        self.url = url
        self.embed_title = embed_title
        self.interaction = interaction
        self.page = 1
        self.av_data = []

    async def get_av_data(self):
        try:
            self.av_data.clear()
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
            driver = webdriver.Chrome(options=options)
            driver.get(f"{self.url}?page={self.page}")
            await asyncio.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            av_list = soup.find_all("div", class_="thumbnail group")
            for av in av_list[:12]:
                image = av.find("img", class_="w-full")["data-src"]
                video = av.find("video", class_="preview hidden")["data-src"]
                length = av.find("span", class_="absolute bottom-1 right-1 rounded-lg px-2 py-1 text-xs text-nord5 bg-gray-800 bg-opacity-75").get_text().strip()
                a_tag = av.find("a", class_="text-secondary group-hover:text-primary")
                link = f"https://missav.com/{a_tag['alt']}"
                number, title = a_tag.get_text().strip().split(" ", 1)
                self.av_data.append({"number": number, "title": title, "length": length, "link": link, "image": image, "video": video})
        except Exception as err:
            print(err)
        finally:
            driver.quit()

    async def create_embed(self):
        embed = discord.Embed(
            title=f"<:MissAV:1308487637975437373> MissAV {self.embed_title}",
            url=self.url,
            colour=discord.Colour.pink(),
            timestamp=datetime.datetime.now()
        )
        for i in range(12):
            try:
                embed.add_field(
                    name=f"【{12 * (self.page - 1) + i + 1:0>2}】［{self.av_data[i]['number']}］（{self.av_data[i]['length']}）",
                    value=f"[{self.av_data[i]['title']}]({self.av_data[i]['link']})",
                    inline=False
                )
            except Exception as err:
                pass
        embed.set_footer(text="NTOU Goblin Engineer 製作")
        return embed

    async def create_view(self):
        view = discord.ui.View(timeout=180)
        view.on_timeout = self.on_timeout
        for i in range(12):
            button = discord.ui.Button(
                label=f"{12 * (self.page - 1) + i + 1:0>2}",
                style=discord.ButtonStyle.blurple,
                custom_id=str(i),
                row=i // 4
            )
            button.callback = self.index_callback
            view.add_item(button)
        last_button = discord.ui.Button(
            label="上一頁",
            style=discord.ButtonStyle.green,
            row=3
        )
        last_button.callback = self.last_callback
        view.add_item(last_button)
        home_button = discord.ui.Button(
            label="回到首頁",
            style=discord.ButtonStyle.gray,
            row=3
        )
        home_button.callback = self.home_callback
        view.add_item(home_button)
        next_button = discord.ui.Button(
            label="下一頁",
            style=discord.ButtonStyle.green,
            row=3
        )
        next_button.callback = self.next_callback
        view.add_item(next_button)
        return view

    async def on_timeout(self):
        embed = discord.Embed(
            title="進入聖人模式",
            colour=discord.Colour.yellow(),
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url="https://www.chinasona.org/Thiaoouba/jesus.jpg")
        embed.set_footer(text="NTOU Goblin Engineer 製作")
        await self.interaction.edit_original_response(embed=embed, view=None)

    async def index_callback(self, interaction: discord.Interaction):
        index = int(interaction.data["custom_id"])
        embed = discord.Embed(
            title=f"【{12 * (self.page - 1) + index + 1:0>2}】［{self.av_data[index]['number']}］（{self.av_data[index]['length']}）",
            description = self.av_data[index]["title"],
            url = self.av_data[index]["link"],
            colour=discord.Colour.pink(),
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url=self.av_data[index]["image"])
        embed.set_footer(text="NTOU Goblin Engineer 製作")
        await interaction.response.edit_message(embed=embed)

    async def last_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page == 1:
            return
        self.page -= 1
        await self.get_av_data()
        embed = await self.create_embed()
        view = await self.create_view()
        await interaction.edit_original_response(embed=embed, view=view)

    async def home_callback(self, interaction: discord.Interaction):
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed)

    async def next_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.page += 1
        await self.get_av_data()
        embed = await self.create_embed()
        view = await self.create_view()
        await interaction.edit_original_response(embed=embed, view=view)

class MissAVCog(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="missav_rank", description="MissAV 排行")
    @discord.app_commands.describe(option="選擇類別")
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
        url = f"https://missav.com/{option.value}"
        miss_av = MissAV(url=url, embed_title=f"{option.name}排行", interaction=interaction)
        await miss_av.get_av_data()
        embed = await miss_av.create_embed()
        view = await miss_av.create_view()
        await interaction.followup.send(embed=embed, view=view)

    @discord.app_commands.command(name="missav_search", description="MissAV 搜尋")
    @discord.app_commands.describe(keyword="使用 + 號結合多個關鍵字")
    async def missav_search(self, interaction: discord.Interaction, keyword: str):
        await interaction.response.defer()
        url = f"https://missav.com/search/{keyword}"
        miss_av = MissAV(url=url, embed_title=f"{keyword}的搜尋結果", interaction=interaction)
        await miss_av.get_av_data()
        embed = await miss_av.create_embed()
        view = await miss_av.create_view()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(MissAVCog(bot))

