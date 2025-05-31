"""
MIDPEM Update Deployment Module.

:author: Max Milazzo
"""


import os
import shutil
import time
import zipfile
from crypto import pki


PROGRAM_DIR = "program"
# current active program directory


ROLLBACK_DIR = "rollback"
# rollback data directory


DEPLOY_DIR = "deploy"
# new deployment directory and zipfile name


PROGRAM_RUN = "man.py"
# program executing starting point


ID_FILE = "id.txt"
# application device identification file
# (present within the current active program)


ERR_MAX = 5
# maximum error count until failure


ERR_WAIT = 10
# time (s) to wait when error encountered


RESERVED_PROGRAM_FILES = [ID_FILE]
# reserved program files that cannot be changed by update manager


def run_retry(func: callable, err_max: int = ERR_MAX, err_wait: int = ERR_WAIT) -> bool:
    """
    Run multiple times and retry on error.
    
    :param func: process to execute
    :param err_max: maximum error count until failure
    :param err_wait: time (s) to wait when error encountered
    
    :return: success status
    """
    
    failures = 0
    # failure counter
    
    while True:
        try:
            func()
            return True
            # return on success
            
        except Exception as e:
            print("FAILURE: " + str(e))
            failures += 1
            
            if failures >= err_max:
                return False
                # return on fatal failure
            
            time.sleep(err_wait)


def unload(rollback: bool) -> tuple:
    """
    Unload deployment data to active program file.
    
    :param rollback: flag specifying whether rollback should be created 
    :return success status, response message
    """
    
    if rollback:
        if os.path.exists(ROLLBACK_DIR):
            shutil.rmtree(ROLLBACK_DIR)
            # delete past rollback directory
            
        shutil.copytree(PROGRAM_DIR, ROLLBACK_DIR)
        # create new rollback directory
    
    for unload_root, dirs, files in os.walk(DEPLOY_DIR):
        program_root = os.path.join(
            PROGRAM_DIR, os.path.relpath(unload_root, DEPLOY_DIR)
        )

        for dir in dirs:
            dir_path = os.path.join(program_root, dir)
            
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
                # copy directories that do not yet exist from deployment
                
        for file in files:
            file_path = os.path.join(program_root, file)
            
            if file in RESERVED_PROGRAM_FILES:
                continue
                # do not allow update to overwrite reserved files
            
            if os.path.exists(file_path):
                os.remove(file_path)
                # delete existing program files to be replaced
                
            if not run_retry(
                lambda: shutil.move(os.path.join(unload_root, file), file_path)
                # move files from deployment
                
            ):
                return False, "%s: [!] UPDATE FAILED"
    
    os.remove(DEPLOY_DIR + ".zip.enc")
    os.remove(DEPLOY_DIR + ".zip")
    # clean up encrypted and uncrypted zipfiles
    
    if not run_retry(
        lambda: shutil.rmtree(DEPLOY_DIR)
        # clean up deployment file
        
    ):
        return False, "%s: [!] UPDATE FAILED"
        
    return True, "%s: [*] UPDATE SUCCESS"


async def deploy(ctx, rollback: bool) -> tuple:
    """
    Deploy new update.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param rollback: flag specifying whether rollback should be created   
    :return success status, response message
    """
    
    file = ctx.message.attachments[0]
    await file.save(DEPLOY_DIR + ".zip.enc")
    # save attachment zip

    pki.decrypt(DEPLOY_DIR + ".zip.enc")
    # decrypts attachment zip (and saves it as .zip)
    
    try:
        with zipfile.ZipFile(DEPLOY_DIR + ".zip", "r") as zip_ref:
            zip_ref.extractall(DEPLOY_DIR)
            # extract attachment zip
        
        return unload(rollback)
        # unload deployment to project directory
        
    except Exception as e:
        print(e)
    
    
def rollback() -> tuple:
    """
    Rollback to previous saved version.
    
    :return success status, response message
    """
    
    if os.path.exists(ROLLBACK_DIR):
    
        if not run_retry(
            lambda: shutil.rmtree(PROGRAM_DIR)
            # remove current program directory
            
        ):
            return False, "%s: [!] ROLLBACK FAILED" 
        
        os.rename(ROLLBACK_DIR, PROGRAM_DIR)
        # set rollback directory to current program directory
        
        return True, "%s: [*] ROLLBACK SUCCESS"
    else:
        return True, "%s: [!] ROLLBACK UNAVAILABLE"