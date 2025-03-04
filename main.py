import os
import json
import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta
from discord import app_commands
from myserver import server_on

SELLER_KEY = "87c3d5a7a8c98996b2cfb1669355406e"  # ใส่ Seller Key ของ KeyAuth
LOG_CHANNEL_ID = 1346431603982729229  # ID ของช่องสำหรับส่ง Log
RESET_HISTORY_FILE = "reset_history.json"  # ไฟล์เก็บข้อมูลการรีเซ็ต

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_reset_history():
    """โหลดข้อมูลการรีเซ็ต HWID จากไฟล์"""
    if os.path.exists(RESET_HISTORY_FILE):
        with open(RESET_HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_reset_history(data):
    """บันทึกข้อมูลการรีเซ็ต HWID ลงไฟล์"""
    with open(RESET_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์แล้ว: {bot.user}")


@bot.command()
@commands.has_role("resetkey")  # ให้เฉพาะ Role "resetkey" ใช้คำสั่งนี้ได้
async def rs(ctx, license_key: str):
    """คำสั่ง !rs <license_key> สำหรับรีเซ็ต HWID ผ่าน KeyAuth"""
    try:
        # โหลดข้อมูลการรีเซ็ตจากไฟล์
        reset_history = load_reset_history()

        # ตรวจสอบว่า License Key นี้เคยถูกรีเซ็ตหรือไม่
        now = datetime.utcnow()
        if license_key in reset_history:
            last_reset = datetime.fromisoformat(reset_history[license_key])
            if now - last_reset < timedelta(days=7):  # ต้องรอ 7 วัน
                if "ASST" not in [role.name for role in ctx.author.roles]:  # ตรวจสอบ Role
                    await ctx.send(f"❌ คีย์ `{license_key}` ถูกรีเซ็ตไปแล้ว กรุณารออีก {7 - (now - last_reset).days} วัน", delete_after=10)
                    return

        # ลบข้อความของผู้ใช้หลังจาก 10 วินาที
        await ctx.message.delete(delay=10)

        # ส่งคำขอไปยัง KeyAuth API
        keyauth_url = f"https://keyauth.win/api/seller/?sellerkey={SELLER_KEY}&type=resetuser&user={license_key}"
        response = requests.get(keyauth_url)
        result = response.json()

        if result.get("success"):
            status = "✅ สำเร็จ"
            message = f"✅ รีเซ็ต HWID ของ `{license_key}` สำเร็จ!"
            reset_history[license_key] = now.isoformat()  # บันทึกวันเวลาการรีเซ็ต
            save_reset_history(reset_history)  # บันทึกลงไฟล์
        else:
            status = f"❌ ล้มเหลว: {result.get('message', 'Unknown error')}"
            message = f"❌ ล้มเหลว: {result.get('message', 'Unknown error')}"

        # ตอบกลับข้อความ (ลบใน 10 วินาที)
        msg = await ctx.send(message)
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
