"""
Remote deployment utility.

:author: Max Milazzo
"""


import base64
import discord
from crypto import pki
from util.config import CONFIG
from discord import SyncWebhook
from discord.ext import commands


POST_LIMIT = 100
# maximum number of PKI posts that can be read


DEPLOY_WEBHOOK = SyncWebhook.from_url(CONFIG["deploy_webhook"])
# deploy webhook that remote update managers can take commands from


PKI_CHANNEL_ID = 123456789012345678
# PKI post channel ID


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(intents=intents)
client.remove_command("help")


@client.event
async def on_ready() -> None:
    """
    Reads PKI posts, generates encrypted zip, and sends update command.
    """

    print("Enter zip file name:")
    zip_file = input("> ")
    # get unencrypted zip file name to deploy

    channel = client.get_channel(PKI_CHANNEL_ID)

    async for message in channel.history(limit=POST_LIMIT):
        try:
            post_cid, public_key_b64 = message.content.split(" ", 1)
            # get computer ID and public key from PKI post
        
        except:
            continue

        if post_cid.lower() in CONFIG["deploy_cids"]:
            public_key = base64.b64decode(public_key_b64)
            pki.encrypt(zip_file, public_key)
            # encrypt zip file using public key for matching device

            with open(zip_file + ".enc", "rb") as f:
                DEPLOY_WEBHOOK.send(content="$update " + post_cid, file=f)
                # deploy update

            await message.delete()
            # delete PKI post


if __name__ == "__main__":
    client.run(CONFIG["token"], log_handler=None)