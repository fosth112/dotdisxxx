@bot.command()
@commands.has_role("resetkey")  # ให้เฉพาะ Role "resetkey" ใช้คำสั่งนี้ได้
async def rs(ctx, license_key: str):
    """คำสั่ง !rs <license_key> สำหรับรีเซ็ต HWID ผ่าน KeyAuth"""
    try:
        # ลบข้อความของผู้ใช้
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("❌ บอทไม่มีสิทธิ์ลบข้อความ กรุณาตรวจสอบสิทธิ์ของบอท", delete_after=10)
            return  # หยุดทำงานถ้าบอทไม่มีสิทธิ์

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
        await ctx.send("❌ บอทไม่มีสิทธิ์ทำงานนี้ กรุณาตรวจสอบสิทธิ์", delete_after=10)
    except commands.MissingRole:
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้", delete_after=10)
