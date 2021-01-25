import asyncio


async def call(cmd, **kwargs):
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, **kwargs
    )
    stdout, _ = await proc.communicate()
    return stdout.decode()
