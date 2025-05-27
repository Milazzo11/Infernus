"""
Update Manager Process Handler.

:author: Max Milazzo
"""


import subprocess
import time
from update_api.deploy import PROGRAM_DIR, PROGRAM_RUN
from util.config import CONFIG
from discord import SyncWebhook


DEPLOY_HELPER_WEBHOOK = SyncWebhook.from_url(CONFIG["man_webhook"])
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