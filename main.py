from telethon import TelegramClient as tg
from telethon.sessions import StringSession
from telethon import events, types
from os important getenv
import traceback, sys, io, asyncio, logging 
from pprint import pprint 

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("logs.txt"), logging.StreamHandler()],
)

API_KEY = int(getenv("API_KEY", 0))
API_HASH = getenv("API_HASH", "")
STRING = getenv("STRING", "")
OWNER_ID = int(getenv("OWNER_ID", 0))

b = tg(StringSession(STRING), API_KEY, API_HASH)

try:
    b.start()
except:
    exit(1)

@b.on(events.NewMessage(outgoing=True, pattern="^.eval (.*?)"))
async def eval(e):
    try:
        a = e.text.split(maxsplit=1)[1]
    except IndexError:
        return await e.edit("`Give some python cmd`")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    ros = sys.stdout = io.StringIO()
    red = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(a, e)
    except Exception:
        exc = traceback.format_exc()
    stdout = ros.getvalue()
    stderr = red.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            a,
            evaluation,
        )
    )
    if len(evaluation) > 4090:
        with io.BytesIO(evaluation.encode()) as finale_b:
            finale_b.name = "eval.txt"
            return await e.respond(f"```{a}```", file=finale_b)
    await eor(e, final_output)


async def aexec(code, event):
    exec(
        f"async def __aexec(e, client): "
        + "\n message = event = e"
        + "\n reply = await event.get_reply_message()"
        + "\n p = print"
        + "".join(f"\n {l}" for l in code.split("\n")),
    )

    return await locals()["__aexec"](event, event.client)


@b.on(events.NewMessage(pattern="(bash|exec)"))
async def __exec(e):
    try:
        cmd = e.text.split(maxsplit=1)[1]
    except IndexError:
        return
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())
    cresult = f"<b>Bash:~#</b> <code>{cmd}</code>\n<b>Result:</b> <code>{result}</code>"
    if len(str(cresult)) > 4090:
        with io.BytesIO(result.encode()) as file:
            file.name = "bash.txt"
            await e.respond(f"<code>{cmd}</code>", file=file, parse_mode="html")
            return await e.delete()
    await e.edit(cresult, parse_mode="html")

b.run_until_disconnected()
