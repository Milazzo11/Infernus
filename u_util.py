"""
Remote deployment utility.

:author: Max Milazzo
"""


import base64
import discord
from crypto import pki
from util.config import CONFIG
from discord import File, SyncWebhook
from discord.ext import commands


POST_LIMIT = 100
# maximum number of PKI posts that can be read


DEPLOY_WEBHOOK = SyncWebhook.from_url(CONFIG["deploy_webhook"])
# deploy webhook that remote update managers can take commands from


DEPLOY_CIDS = [cid.lower() for cid in CONFIG["deploy_cids"]]
# lowercase deploy computer IDs


CMD_PREFIX = "$"
# command prefix


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)
client.remove_command("help")
# create and set up bot


@client.event
async def on_ready() -> None:
    """
    Reads PKI posts, generates encrypted zip, and sends update command.
    """

    print("Enter zip file name:")
    zip_file = input("> ")
    # get unencrypted zip file name to deploy

    channel = client.get_channel(CONFIG["pki_channel_id"])

    async for message in channel.history(limit=POST_LIMIT):
        try:
            post_cid, public_key_b64 = message.content.split(" ", 1)
            # get computer ID and public key from PKI post
        
        except:
            continue
        
        ## DISCARD NOT MOST RECENT CID POST IF EXISTS (AND DELETE IT)
        if post_cid.lower() in DEPLOY_CIDS:
            public_key = base64.b64decode(public_key_b64)
            pki.encrypt(zip_file, public_key)
            # encrypt zip file using public key for matching device

            with open(zip_file + ".enc", "rb") as f:
                file = File(f, filename=zip_file + ".enc")
                DEPLOY_WEBHOOK.send(content="$update " + post_cid, file=file)
                # deploy update

            await message.delete()
            # delete PKI post
    
    await client.close()
    # end program


if __name__ == "__main__":
    client.run(CONFIG["token"], log_handler=None)