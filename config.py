import re

from subprocess import run
from os.path import expanduser
from widgets import *

def spawn(program, *args):
    run(["herbstclient", "spawn", program, *args], shell=False)

# ---------------------------------------------------

def ip_addr():
    out = run(["ip", "a"],
              shell=False,
              capture_output=True,
              text=True).stdout

    ip = re.search("wlp1s0.*inet (\\d+.\\d+.\\d+.\\d+)/", out, re.DOTALL)

    return ip.group(1)

ip = Box([FColor(Text(ip_addr()), "#c9a00e"), FColor()])

# ---------------------------------------------------

logo = Button(Offset(Box([
    FColor(
        Font(
            Text('\uf303'), "4"),
        "#1693d2"),
    FColor()
], ''), "4"), lambda: spawn(expanduser("~/.local/bin/menu.sh")))

left_box = Box([logo], ' ')

# ---------------------------------------------------

clock = Clock()

right_box = Box([
    ip,
    Volume(lambda: spawn("pavucontrol"), 2),
    BatteryBox(2),
    Button(clock, lambda: clock.toggle())
], ' | ')

# ---------------------------------------------------

fonts = [
    "Galmuri7-12",
    "Font Awesome 6 Free Solid-12",
    "Font Awesome 6 Brands-12",
    "font\\-logos"
]

bar = Box([
    AlignLeft(left_box),
    AlignRight(right_box)
], '')
