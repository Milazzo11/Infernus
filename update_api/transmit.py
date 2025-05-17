"""
MIDPEM Remote Controller Transmitter.
(implemented for use as update response transmitter)

:author: Max Milazzo
"""


async def transmit(ctx, msg: str, files: list = None, no_cmd: bool = False) -> None:
    """
    Manage response and transmit to remote controller.
    
    :param ctx: command context
    :type ctx: Discord context object
    :param msg: response message
    :param files: response message file attachments
    """
    
    if not no_cmd:
        print("\n<cmd>  " + ctx.message.content)
        # display command input to console
        
    else:
        print()
        # print newline padding
    
    print("<res>  " + msg + "\n")
    # display response info to console
    
    msg = msg.replace("*", "✓")
    # format message to send to server
    
    await ctx.reply(msg, files=files)
    # send resonse to server