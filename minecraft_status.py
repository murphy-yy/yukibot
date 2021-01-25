import asyncio
from concurrent.futures import ThreadPoolExecutor

from mcstatus import MinecraftServer

executor = ThreadPoolExecutor()


def clean_description(o):
    if isinstance(o, dict):
        if "extra" in o.keys():
            return "".join(map(lambda x: x["text"], o["extra"]))
        else:
            return o["text"]
    else:
        return o


def information(sample):
    return "\n".join(map(lambda p: p.name, sample or []))


def _connect(address):
    server = MinecraftServer.lookup(address)
    status = server.status()
    status.clean_description = clean_description(status.description)
    status.information = information(status.players.sample)
    return status


async def connect(address):
    loop = asyncio.get_event_loop()
    status = await loop.run_in_executor(executor, _connect, address)
    return status
