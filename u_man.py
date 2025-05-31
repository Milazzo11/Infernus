"""
Secure (encrypted) MIDPEM Update Manager.

:author: Max Milazzo
"""


import discord
import os
import shlex
from crypto import pki
from util.process import kill_sig, start_sig
from update_api import deploy
from update_api.transmit import transmit
from util.config import CONFIG
from discord.ext import commands
from typing import Union


with open(os.path.join(deploy.PROGRAM_DIR, deploy.ID_FILE)) as f:
    COMPUTER_ID = f.read()
    # computer identification string


CMD_PREFIX = "$"
# command prefix


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)
client.remove_command("help")
# create and set up bot


@client.command(name="update", aliases=["up"])
async def _update(ctx, device_id: str, raw: str = "-", reset_pki: str = "-") -> None:
    """
    Device-specific update initiation command signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param device_id: command execution device identifier
    :param raw: "raw" update flag -- kill and restart system if not present,
        otherwise perform a simple file inclusion/replacement with no restart
        or rollback directory creation (can be dangerous if improperly used)
    :param reset_pki: "noreset" PKI reset disable flag -- reset PKI keys and
        post as normal if not present, otherwise do not reset keys 
    """

    if device_id.lower() == COMPUTER_ID.lower():
        await transmit(ctx, f"{COMPUTER_ID}: [i] UPDATE SIGNAL RECEIVED")
        
        kill = (raw.lower() != "raw")
        pki_reset = (reset_pki.lower() != "noreset")
        
        if kill:
            kill_sig(COMPUTER_ID)
            # stop current process on update signal receipt

        success, res = await deploy.deploy(ctx, rollback=kill)
        # deploy update
        
        if pki_reset:
            pki.setup(COMPUTER_ID)
            # reset assymetric key pair

        if kill and success:
            start_sig()
            # start new process if update successful (and previously killed)

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

    pki.setup(COMPUTER_ID)
    # reset assymetric key pair

    if success:
        start_sig()
        # start new process if update successful

    await transmit(ctx, res % COMPUTER_ID)


@client.command(name="rollback", aliases=["rb"])
async def _rollback(ctx, device_id: str) -> None:
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
async def _rollback_all(ctx) -> None:
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
async def _status(ctx, device_id: Union[str, None] = None) -> None:
    """
    Device-specific AND Universal status query signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param device_id: command execution device identifier
    """

    if device_id is None or device_id.lower() == COMPUTER_ID.lower():
        await transmit(ctx, f"{COMPUTER_ID}: [i] ONLINE")


@client.command(name="statusall", aliases=["ssa"])
async def _status_all(ctx) -> None:
    """
    Universal status query signal.
    
    :param ctx: command context
    :type ctx: Discord context object
    """

    await transmit(ctx, f"{COMPUTER_ID}: [i] ONLINE")


@client.event
async def on_message(message) -> None:
    """
    Directly handle messages to allow other bots and webhooks to interface with
    the update manager and send their own commands.
    
    :param message: server message
    :type message: Discord message object
    """

    if message.author == client.user:
        return
        # exit on current bot message read

    if message.author.bot:
    # allow webhook and bot commands to be processed
    
        command_text = shlex.split(message.content)
        command = client.get_command(command_text[0].replace(CMD_PREFIX, ""))
        ctx = await client.get_context(message)
        # process input command and get context
        
        if len(command_text) == 1:
            await command(ctx)
            # process 0 argument command
            
        else:
            await command(ctx, *command_text[1:])
            # process 1+ argument command

    else:
        await client.process_commands(message)
        # process user commands normally
        # (this allows error detection and messaging to stay on)


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
    pki.setup(COMPUTER_ID)
    client.run(CONFIG["token"], log_handler=None)