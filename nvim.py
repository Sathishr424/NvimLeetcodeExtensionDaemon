import json
import asyncio
import subprocess
import pynvim
import os

REGISTRY_PATH = os.path.join(os.getcwd(), "registries.json")

class NvimHandler:
    def __init__(self):
        pass

    def get_active_pane(self):
        """
        Returns the active pane from the active window.

        Works when executed outside tmux.
        """

        output = subprocess.check_output(
            [
                "tmux",
                "list-panes",
                "-a",
                "-F",
                "#{session_name} #{window_active} #{pane_active} #{pane_id}",
            ],
            text=True,
        )

        for line in output.splitlines():
            session, window_active, pane_active, pane_id = line.split()

            if window_active == "1" and pane_active == "1":
                return pane_id

        return None

    def load_registry(self):
        with open(REGISTRY_PATH) as f:
            return json.load(f)

    def find_nvim(self, registry, pane):
        for info in registry.values():
            if info["pane"] == pane:
                return info
        return None

    async def send(self, data):
        pane = self.get_active_pane()

        if pane is None:
            print("No active tmux pane found.")
            return

        registry = self.load_registry()

        info = self.find_nvim(registry, pane)
        if info is None:
            print(f"No Neovim registered for pane {pane}")
            return

        print("Info:", info)
        await asyncio.to_thread(self._send_to_nvim, info, data)

    def _send_to_nvim(self, info, data):
        nvim = pynvim.attach("socket", path=info["socket"])

        # Example commands
        # nvim.command("echo " + str(data))
        # nvim.command("normal! G")
        nvim.exec_lua(
            "require('leetcode.commands').createFile(...)",
            data,
        )
