import asyncio
import tempfile


async def call(cmd, **kwargs):
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, **kwargs
    )
    stdout, _ = await proc.communicate()
    return stdout.decode()


async def call_in_tmpdir(cmd):
    with tempfile.TemporaryDirectory() as tmpdir:
        await call(cmd, cwd=tmpdir)
