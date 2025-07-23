import json
import aiohttp
import discord
from discord.ext import tasks
from config import DISCORD_TOKEN, CHANNEL_NAME, PLAYER_IDS

CACHE_FILE = "cache.json"

class GGSTBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.cache = {}
        self.load_cache()

    def load_cache(self):
        try:
            with open(CACHE_FILE, "r") as f:
                self.cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    def save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f)

    async def setup_hook(self):
        self.poll_matches.start()

    @tasks.loop(minutes=5)
    async def poll_matches(self):
        channel = discord.utils.get(self.get_all_channels(), name=CHANNEL_NAME)
        if channel is None:
            print(f"Channel '{CHANNEL_NAME}' not found")
            return

        async with aiohttp.ClientSession() as session:
            for name, player_id in PLAYER_IDS.items():
                await self.check_player(session, channel, name, player_id)

        self.save_cache()

    async def check_player(self, session: aiohttp.ClientSession, channel: discord.TextChannel, name: str, player_id: str):
        url = f"https://puddle.farm/api/player/{player_id}/matches?take=5"
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Failed to fetch matches for {name}: {resp.status}")
                return
            matches = await resp.json()

        player_cache = self.cache.setdefault(player_id, [])
        for match in reversed(matches):
            match_id = str(match.get("id"))
            if match_id not in player_cache:
                opponent = match["opponent"]["name"]
                opponent_char = match["opponent"]["character"]
                char = match["character"]
                result = match["result"]
                score = match["score"]
                change = match["change"]
                action = "vient de gagner contre" if result == "win" else "vient de perdre contre"
                message = (
                    f"{name} ({char}) {action} {opponent} ({opponent_char})"
                    f" — Score {score}, {change:+} pts"
                )
                await channel.send(message)
                player_cache.append(match_id)
        self.cache[player_id] = player_cache[-20:]

intents = discord.Intents.default()
bot = GGSTBot(intents=intents)
bot.run(DISCORD_TOKEN)
