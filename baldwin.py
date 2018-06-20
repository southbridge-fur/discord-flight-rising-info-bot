import discord
from discord.ext import commands
import asyncio
import re

class Baldwin:
    """double, double, toil and trouble; fire burn and cauldron bubble."""

    timeRe = re.compile(r'(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?')

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def brew(self, context, time):
        """Given a time in NhNm format, alerts user when that amount of time has passed."""
        duration = self.parse_duration(time)
        self.bot.loop.create_task(self.reminder(
            duration * 60,
            context.message.author,
            "YOUR BALDWIN BREW IS DONE. NOW, GET BACK TO WORK."))
        await self.bot.say("I'LL REMIND YOU ABOUT YOUR BREW IN {0} MINUTES.".format(duration))

    @commands.command(pass_context = True)
    async def transmute(self, context):
        """Alerts user after 30 minutes."""
        self.bot.loop.create_task(self.reminder(
            30 * 60,
            context.message.author,
            "YOUR TRANSMUTATION IS DONE. IS THIS SUPPOSED TO BE COFFEE?"))
        await self.bot.say("I'LL REMIND YOU ABOUT YOUR BREW IN 30 MINUTES.")

    async def reminder(self, duration, user, message):
        await asyncio.sleep(duration)
        await self.bot.send_message(user, message)

    def parse_duration(self, time):
        match = self.timeRe.match(time)
        if match is None:
            return 0
        hours = match.group('hours') or 0
        minutes = match.group('minutes') or 0
        return int(hours) * 60 + int(minutes)

def setup(bot):
    bot.add_cog(Baldwin(bot))