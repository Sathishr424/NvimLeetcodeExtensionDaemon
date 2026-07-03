import asyncio
import json
import os
from server import Server

SOCKET = "/tmp/nvim-daemon.sock"

registry = {}
def writeRegistry():
    with open("registries.json", 'w', encoding='utf-8') as file:
        file.write(json.dumps(registry))

async def handle(reader, writer):
    line = await reader.readline()

    data = json.loads(line.decode())

    registry[data["pane"]] = data
    writeRegistry()

    print("Registered:", data)

    writer.close()

async def main():
    if os.path.exists(SOCKET):
        os.unlink(SOCKET)

    server = await asyncio.start_unix_server(handle, SOCKET)

    api_server = Server(registry)
    await api_server.start()

    async with server:
        await server.serve_forever()


asyncio.run(main())
