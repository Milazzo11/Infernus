"""
INFERNUS x MIDPEM Update Manager.

:author: Max Milazzo
"""


import os
import time
import discord
from crypto.asymmetric import AKE
from update_api import deploy
from update_api.transmit import transmit
from process import kill_sig, start_sig
from discord import SyncWebhook
from discord.ext import commands


with open("token.txt", "r") as f:
    TOKEN = f.read()
    # Discord bot interface token

with open("webhook.txt", "r") as f:
    PKI_WEBHOOK = SyncWebhook.from_url(f.read())
    # PKI post webhook

with open(os.path.join(deploy.PROGRAM_DIR, deploy.ID_FILE)) as f:
    COMPUTER_ID = f.read()
    # get computer identification

CMD_PREFIX = "$"
# command prefix

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)
client.remove_command("help")
# create and set up bot


@client.command(name="update", aliases=["up"])
async def _update(ctx, device_id) -> None:
    """
    Device-specific update initiation command signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param device_id: command execution device identifier
    """
    
    if device_id.lower() == COMPUTER_ID.lower():
        await transmit(ctx, f"{COMPUTER_ID}: [i] UPDATE SIGNAL RECEIVED")
        kill_sig(COMPUTER_ID)
        # stop current process on update signal receipt
        
        success, res = await deploy.deploy(ctx)
        # deploy update
        
        if success:
            start_sig()
            # start new process if update successful
            
        await transmit(ctx, res % COMPUTER_ID)
    
    
@client.command(name="updateall", aliases=["upa"])
async def _update_all(ctx) -> None:
    """
    Universal update initiation command signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    """

    await transmit(ctx, f"{COMPUTER_ID}: [i] UPDATE SIGNAL RECEIVED")
    kill_sig(COMPUTER_ID)
    # stop current process on update signal receipt
    
    success, res = await deploy.deploy(ctx)
    # deploy update
    
    if success:
        start_sig()
        # start new process if update successful
        
    await transmit(ctx, res % COMPUTER_ID)
    
    
@client.command(name="rollback", aliases=["rb"])
async def _rollback(ctx, device_id) -> None:
    """
    Device-specific rollback initiation command signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param device_id: command execution device identifier
    """
    
    if device_id.lower() == COMPUTER_ID.lower():
        await transmit(ctx, f"{COMPUTER_ID}: [i] ROLLBACK SIGNAL RECEIVED")
        kill_sig(COMPUTER_ID)
        # stop current process on rollback signal receipt
        
        success, res = deploy.rollback()
        # initiate rollback
        
        if success:
            start_sig()
            # start new process if rollback successful
            
        await transmit(ctx, res % COMPUTER_ID)
        
        
@client.command(name="rollbackall", aliases=["rba"])
async def _rollback(ctx) -> None:
    """
    Universal rollback initiation command signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    """
    
    await transmit(ctx, f"{COMPUTER_ID}: [i] ROLLBACK SIGNAL RECEIVED")
    kill_sig(COMPUTER_ID)
    # stop current process on rollback signal receipt
    
    success, res = deploy.rollback()
    # initiate rollback
    
    if success:
        start_sig()
        # start new process if rollback successful
        # (or if unavailable, but no failure occurred)
        
    await transmit(ctx, res % COMPUTER_ID)

    
@client.command(name="status", aliases=["ss"])
async def _status(ctx, device_id=None) -> None:
    """
    Device-specific AND Universal status query signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param device_id: command execution device identifier
    """
    
    if device_id is None or device_id.lower() == COMPUTER_ID.lower():
        await transmit(ctx, f"{COMPUTER_ID}: [i] ONLINE")
        
        
@client.command(name="statusall", aliases=["ssa"])
async def _status_all(ctx, device_id=None) -> None:
    """
    Universal status query signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param device_id: command execution device identifier
    """
    
    await transmit(ctx, f"{COMPUTER_ID}: [i] ONLINE")


@client.event
async def on_command_error(ctx, error) -> None:
    """
    Command error handler.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param error: error
    :type error: Discord error object
    """
    
    await ctx.reply(COMPUTER_ID + ": " + str(error))


@client.event
async def on_ready() -> None:
    """
    Display console message on startup.
    """
    
    print("U-MAN: [listener active]\n")


if __name__ == "__main__":  
    client.run(TOKEN, log_handler=None)
