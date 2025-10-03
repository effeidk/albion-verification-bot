import discord
from discord.ext import commands, tasks
import aiohttp
import os

# Il token va messo come variabile d'ambiente su Railway con nome "TOKEN"
TOKEN = os.getenv("TOKEN")

# ID gilda Albion (UUID)
GUILD_ID_ALBION = "3Ldk-pk4R-inDVgxklnn9Q"

# ID ruolo Discord (numero intero)
ROLE_ID = 1398774088612188190

# ID server Discord (numero intero)
GUILD_ID_DISCORD = 1398773662114648134

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

verified_members = {}

async def is_member_of_guild(ign):
    url = f"https://gameinfo.albiononline.com/api/gameinfo/guilds/{GUILD_ID_ALBION}/members"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                for member in data:
                    if member["Name"].lower() == ign.lower():
                        return True
    return False

@bot.event
async def on_ready():
    print(f"✅ Bot online come {bot.user}")
    check_guild_status.start()

@bot.command()
async def verifica(ctx, ign: str):
    await ctx.send(f"🔍 Verifica in corso per `{ign}`...")
    if await is_member_of_guild(ign):
        member = ctx.author
        verified_members[member.id] = ign
        try:
            await member.edit(nick=ign)
        except discord.Forbidden:
            await ctx.send("⚠️ Non posso cambiare il nickname.")

        role = discord.utils.get(ctx.guild.roles, id=ROLE_ID)
        if role:
            await member.add_roles(role)
            await ctx.send(f"✅ Verificato! Ruolo assegnato a `{ign}`.")
        else:
            await ctx.send("❌ Ruolo non trovato.")
    else:
        await ctx.send("❌ IGN non trovato nella gilda.")

@tasks.loop(minutes=10)
async def check_guild_status():
    print("🔁 Controllo membri...")
    to_remove = []
    for discord_id, ign in verified_members.items():
        if not await is_member_of_guild(ign):
            to_remove.append(discord_id)

    guild = bot.get_guild(GUILD_ID_DISCORD)
    role = guild.get_role(ROLE_ID)

    for discord_id in to_remove:
        member = guild.get_member(discord_id)
        if member and role in member.roles:
            await member.remove_roles(role)
            await member.edit(nick=None)
            print(f"❌ {member} rimosso dalla gilda")
            del verified_members[discord_id]

bot.run(TOKEN)
