from aiohttp import web
import subprocess
from nvim import NvimHandler

class Server:
    def __init__(self, registry={}):
        self.registry = registry
        self.port = 8765

    def _kill_process_on_port(self, port: int):
        try:
            # Find the PID listening on the port
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"],
                capture_output=True,
                text=True,
                check=False,
            )

            pids = result.stdout.strip().splitlines()

            for pid in pids:
                print(f"Killing process {pid} using port {port}")
                subprocess.run(["kill", "-9", pid], check=False)

        except Exception as e:
            print(f"Failed to free port {port}: {e}")


    async def open_problem(self, request):
        try:
            data = await request.json()
            await NvimHandler().send(self.registry, data)
            return web.Response(text="ok")
        except Exception as e:
            print("Error response:", e)
            return web.Response(text="server error")

    async def start(self):
        self._kill_process_on_port(self.port)

        app = web.Application()
        app.router.add_post("/open", self.open_problem)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "127.0.0.1", self.port)
        try:
            await site.start()
        except OSError as e:
            if e.errno == 98:
                print("Server is already running.")
                return
            raise

        print(f"HTTP server listening on {self.port}")
