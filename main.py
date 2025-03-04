import os
import discord
from discord.ext import commands
import requests
from discord import app_commands
from myserver import server_on

SELLER_KEY = "87c3d5a7a8c98996b2cfb1669355406e"  # ใส่ Seller Key ของ KeyAuth
LOG_CHANNEL_ID = 1346431603982729229  # ใส่ ID ของช่องที่ต้องการให้บอทส่ง Log

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์แล้ว: {bot.user}")


@bot.command()
@commands.has_role("resetkey")  # ให้เฉพาะ Role "resetkey" ใช้คำสั่งนี้ได้
async def reset_hwid(ctx, license_key: str):
    """คำสั่ง !reset_hwid <license_key> สำหรับรีเซ็ต HWID ผ่าน KeyAuth"""
    try:
        # ลบข้อความของผู้ใช้หลังจาก 10 วินาที
        await ctx.message.delete(delay=10)

        keyauth_url = f"https://keyauth.win/api/seller/?sellerkey={SELLER_KEY}&type=resetuser&user={license_key}"
        response = requests.get(keyauth_url)
        result = response.json()

        if result.get("success"):
            msg = await ctx.send(f"✅ รีเซ็ต HWID ของ `{license_key}` สำเร็จ!")
            status = "✅ สำเร็จ"
        else:
            msg = await ctx.send(f"❌ ล้มเหลว: {result.get('message', 'Unknown error')}")
            status = f"❌ ล้มเหลว: {result.get('message', 'Unknown error')}"

        # ลบข้อความของบอทหลังจาก 10 วินาที
        await msg.delete(delay=10)

        # ส่ง Log ไปยังช่องที่กำหนด
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📋 Log การใช้งานรีเซ็ต HWID", color=0x00ff00)
            embed.add_field(name="👤 ผู้ใช้งาน", value=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})", inline=False)
            embed.add_field(name="🔑 License Key", value=license_key, inline=False)
            embed.add_field(name="📅 เวลาที่ใช้คำสั่ง", value=discord.utils.format_dt(ctx.message.created_at, style="F"), inline=False)
            embed.add_field(name="📌 สถานะ", value=status, inline=False)
            await log_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ บอทไม่มีสิทธิ์ลบข้อความ", delete_after=10)
    except commands.MissingRole:
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้", delete_after=10)


server_on()

bot.run(os.getenv('TOKEN'))
