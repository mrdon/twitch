import json
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class Window:
    title: str
    class_name: str

class Api:
    def get_windows(self) -> List[Window]:
        output = _exec("""
        global              
      .get_window_actors()
      .map(a=>a.meta_window)                                   
      .map(w=>({class: w.get_wm_class(), title: w.get_title()}))
        """)

        for item in json.loads(output[8:-3]):
            yield Window(title=item["title"], class_name=item["class"])




def _exec(script: str):
    process = subprocess.run([
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.gnome.Shell",
        "--object-path",
        "/org/gnome/Shell",
        "--method",
        "org.gnome.Shell.Eval",
        script
    ],
                             stdout=subprocess.PIPE,
                         universal_newlines=True)
    if process.returncode == 1:
        print(f"Error: {process.stderr}")
        exit(1)
    else:
        return process.stdout


api = Api()
windows = list(api.get_windows())

print(f"windows: {windows}")