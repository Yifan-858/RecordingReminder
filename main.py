import os
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from dotenv import load_dotenv
import requests
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NINJA_API_KEY = os.getenv("NINJA_API_KEY")

intents = discord.Intents.default()
intents.message_content= True

bot = commands.Bot(command_prefix="!", intents = intents)

reminder_active = True
scheduled_reminder_sent = False
reminder_message = None
reminder_view = None

def get_fun_fact():
    try:
      r = requests.get("https://api.api-ninjas.com/v1/facts", headers={"X-Api-Key":NINJA_API_KEY },timeout=5)
      
      if r.status_code == 200:
        data = r.json()
        return data[0]["fact"]
      else:
        return "Cannot fetch fun fact."
    except Exception:
      return f"Exception: {Exception}"
    
class ReminderView(View):
  def __init__(self):
     super().__init__(timeout=None)
     self.button = discord.ui.Button(label="It's time to remind!", style= discord.ButtonStyle.danger, custom_id="remind_start")
     self.button.callback = self.button_clicked
     self.add_item(self.button)
     
  async def button_clicked(self, interaction: discord.Interaction):
      global reminder_active
      reminder_active = False
      
      self.button.disabled = True
      await interaction.response.edit_message(view = self)
      
      fact = get_fun_fact()
      await interaction.followup.send(f"Robin is reminded. A fun fact for today: {fact}", ephemeral=False)

#Testing
@bot.command()
@commands.has_permissions(administrator=True)
async def post_reminder(ctx):
  view = ReminderView()
  await ctx.send("Has the lession started? Remind Robin to record.", view=view)
  
TESTING_CHANNEL_ID = 1412418474751430798 # private testing channel 
CLASS_CHANNEL_ID = 1409835563275653142 # class allmänt channel 


sweden_timezone = ZoneInfo("Europe/Stockholm")
POST_TIMES = [(9, 15), (13, 10)]
                      

@tasks.loop(minutes=0.2) # testing, change the minutes later
async def scheduled_reminder():
    global reminder_active
    global scheduled_reminder_sent
    global reminder_message
    global reminder_view
    
    now_local = datetime.now(sweden_timezone)
    # weekday = now_local.weekday()
    
    # if weekday in [1, 3]:
    print(f"Checking time: {now_local.hour}:{now_local.minute}")
    
    for hour, minute in POST_TIMES:
      if not scheduled_reminder_sent and now_local.hour == hour and now_local.minute == minute:
        print("Posting scheduled reminder!")
        
        #Testing if class channel exists
        channel_to_sent = []
        
        testing_channel = bot.get_channel(TESTING_CHANNEL_ID)
        if testing_channel:
          channel_to_sent.append(testing_channel)
        
        class_channel = bot.get_channel(CLASS_CHANNEL_ID)
        if class_channel:
          channel_to_sent.append(class_channel)
          
        reminder_view = ReminderView()
        
        for channel in channel_to_sent:
              await channel.send("Has the lession started? Remind Robin to record.", view=reminder_view)
          
        scheduled_reminder_sent = True # improve input with 2 buttons y/n
        break;
              
      # elif scheduled_reminder_sent and reminder_active:
      #   if reminder_message: 
      #     await reminder_message.edit(content = "Maybe now ⏰? Remind Robin to record.", view= reminder_view)
      #     print("Reminder reposted!")
          
@bot.event
async def on_ready():
  print(f"Logged in as {bot.user}")
  await asyncio.sleep(5)
  scheduled_reminder.start()
  
bot.run(DISCORD_TOKEN)