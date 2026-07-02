import asyncio
import json
import os
from server import Server

SOCKET = "/tmp/nvim-daemon.sock"
REGISTRY_PATH = 'registries.json'

def writeRegistry(data):
    with open("registries.json", 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, indent=2))

def readRegistry():
    with open("registries.json", 'r', encoding='utf-8') as file:
        data = file.read()
        if len(data) == 0: data = "{}"
        return json.loads(data)

if not os.path.exists(REGISTRY_PATH):
    writeRegistry({})

registry = readRegistry()

async def handle(reader, writer):
    line = await reader.readline()

    data = json.loads(line.decode())

    for pid in list(registry.keys()):
        if pid in registry and registry[pid]['pane'] == data['pane']:
            del registry[pid]
            registry[data['pid']] = data
            break
    else:
        registry[data["pid"]] = data

    print("Registered:", data)
    writeRegistry(registry)

    writer.close()

async def main():
    if os.path.exists(SOCKET):
        os.unlink(SOCKET)

    server = await asyncio.start_unix_server(handle, SOCKET)

    api_server = Server()
    await api_server.start()

    async with server:
        await server.serve_forever()


asyncio.run(main())
