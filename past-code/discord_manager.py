import discord
from discord.ext import tasks, commands
import json
import messenger
from keys import key

bot = commands.Bot(command_prefix="")
    
@bot.event
async def on_ready():
    print("Logged in")
    updater.start()


@tasks.loop(seconds=60)
async def updater():
    try:
        noti = bot.get_channel(853110820611555328)
        announcements = bot.get_channel(864949029623169044)
        message = messenger.get_message()

        if len(message["trades"])>0:
            try:
                for trade in message["trades"]:
                    action = "Liquidate" if trade["liquidate"] else "Trade"
                    await announcements.send(f"{action} long position: {trade['long']}, and short position {trade['short']}")
                    message["trades"] = []
                    messenger.save_message(message)
            except:
                await announcements.send("Action performed but is corrupted")
    except:
        pass

@bot.command()
async def portfolio(message):
    '''returns portfolio worth'''
    portfolio = messenger.get_message()["portfolio"]
    await message.channel.send(f"Current USDT: {str(round(portfolio['usdt'], 2))}, total: {str(round(portfolio['total'], 2))}")
    start()
    
@bot.command()
async def summary(message, strat=None):
    """Gives summary of all positions"""
    m = messenger.get_message()
    if strat is None:
        for strat in m["strategy"]:
            summary = m["strategy"][strat]
            await message.channel.send(f"{strat} occupies {str(round(summary['pct']*100, 2))}% of portfolio, with asset worths {str(round(summary['a'], 2))} and {str(round(summary['b'], 2))}")
    else:
        try:
            summary = m["strategy"][strat.upper()]
            await message.channel.send(f"{strat.upper()} occupies {str(round(summary['pct']*100, 2))}% of portfolio, with asset worths {str(round(summary['a'], 2))} and {str(round(summary['b'], 2))}")
        except:
            await message.channel.send(f"No summary available for strat {strat}")
    start()
            
@bot.command()
async def strat(message, strat=None):
    """lists all the stats of strat"""
    m = messenger.get_message()
    if strat is None:
        await message.channel.send("Please enter a strategy")
    else:
        try:
            strategy = m["strategy"][strat.upper()]
            string = ""
            for k in strategy:
                string += f"{k}: {strategy[k]}\n"
            await message.channel.send(string)
        except:
            await message.channel.send(f"No summary available for strat {strat}")
    start()
            
@bot.command()
async def z(message):
    """lists the z-scores of all strats"""
    m = messenger.get_message()
    string = ""
    for strat in m["strategy"]:
        z = m["strategy"][strat]["z"]
        string += f"{strat}: {round(z, 2)}\n"
    await message.channel.send(string)
    start()
            
@bot.command()
async def status(message):
    """returns time of last printer update"""
    m = messenger.get_message()
    try:
        await message.channel.send(m["last_update"])
    except:
        await message.channel.send("Model never ran before")
    start()
        
def start():
    """attempts to start loop"""
    try:
        updater.start()
        print("Restart loop")
    except:
        pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

@updater.before_loop
async def before():
    await bot.wait_until_ready()
    
bot.run(key("discord", "api"))

