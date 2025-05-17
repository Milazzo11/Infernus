"""
Update Manager Process Handler.

:author: Max Milazzo
"""


import os
import time
import subprocess
from update_api.deploy import PROGRAM_DIR, PROGRAM_RUN
from discord import SyncWebhook


DEPLOY_HELPER_WEBHOOK = SyncWebhook.from_url(
    "https://discordapp.com/api/webhooks/1153815910939897897/V7YYNCN2rQNeVG3DcMfWXo5h-em0_lRcoYtYMrIwUVLd4MUbtqY5oyOhNSa6uX_Omki2"
)
# deploy helper webhook to send commands to MIDPEM bots


KILL_CMD = "$systemoff %s"
# MIDPEM system kill command


SIGNAL_WAIT = 10
# wait time after kill command executed


def kill_sig(device_id: str) -> None:
    """
    Kill MIDPEM.
    
    :param device_id: command execution device identifier
    """
    
    DEPLOY_HELPER_WEBHOOK.send(KILL_CMD % device_id)
    time.sleep(SIGNAL_WAIT)
    
    
def start_sig() -> None:
    """
    Start MIDPEM.
    """
    
    subprocess.Popen(["py", PROGRAM_RUN], cwd=PROGRAM_DIR, shell=True)