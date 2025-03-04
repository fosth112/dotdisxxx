import os
import discord
from discord.ext import commands
import requests
from discord import app_commands
from myserver import server_on


SELLER_KEY = "87c3d5a7a8c98996b2cfb1669355406e"  # ใส่ Seller Key ของ KeyAuth

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์แล้ว: {bot.user}")


@bot.command()
async def reset_hwid(ctx, license_key: str):
    """คำสั่ง !reset_hwid <license_key> สำหรับรีเซ็ต HWID ผ่าน KeyAuth"""
    keyauth_url = f"https://keyauth.win/api/seller/?sellerkey={SELLER_KEY}&type=resetuser&user={license_key}"

    response = requests.get(keyauth_url)
    result = response.json()

    if result.get("success"):
        await ctx.send(f"✅ รีเซ็ต HWID ของ `{license_key}` สำเร็จ!")
    else:
        await ctx.send(f"❌ ล้มเหลว: {result.get('message', 'Unknown error')}")
        
server_on()

bot.run(os.getenv('TOKEN'))
