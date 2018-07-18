
import i3ipc
from sys import argv
from math import floor


if argv[1] == "tabs_outliner":
    from sh import chromium
elif argv[1] == "rover":
    from time import sleep
else:
    raise Exception("Unrecognized target " + argv[1])


# Main function
def toggle_pin(
    target = argv[1],
    left_margin = int(argv[2]), # 10
    desired_width = int(argv[3]) # 450
):
    i3 = i3ipc.Connection()
    current_workspace = i3.get_tree().find_focused().workspace()

    windows = {
        "tabs_outliner" : pinnable_window(i3, "tabs_outliner"),
        "rover" : pinnable_window(i3, "rover")
    }

    other = {
        "tabs_outliner" : "rover",
        "rover" : "tabs_outliner"
    }

    other = windows[other[target]]
    target = windows[target]
    
    if other.is_running and (other.window.workspace().name == current_workspace.name):
        other.window.command("move scratchpad")

    if target.is_running and (target.window.workspace().name == current_workspace.name):
        target.window.command("move scratchpad")
        return

    if not target.is_running:
        target.start()

    pin(target, current_workspace, left_margin, desired_width)


class pinnable_window:
    def __init__(self, connection, _type):
        self.connection = connection
        self._type = _type

        if _type == "tabs_outliner":
            self.window = self._find_tabs_outliner()
        elif _type == "rover":
            self.window = self._find_rover()

        self.is_running = bool(self.window)


    def relocate(self):
        if self._type == "tabs_outliner":
            self.window = self._find_tabs_outliner()
        elif self._type == "rover":
            self.window = self._find_rover()


    def start(self):
        if self._type == "tabs_outliner":
            chromium("--app=chrome-extension://eggkanocgddhmamlbiijnphhppkpkmkl/activesessionview.html")
            self.window = _find_tabs_outliner()

        elif self._type == "rover":
            self.connection.command("exec /home/keith/dotfiles/environment/i3-scripts/terminal.sh rover --name=rover_panel")
            sleep(0.095) # TODO : This is Hacky
            self.window = self._find_rover()
        
        self.is_running = True


    def _find_tabs_outliner(self):
        tree = self.connection.get_tree()

        # look for script-opened TabsOutliner window in tree first
        windows = tree.find_instanced("eggkanocgddhmamlbiijnphhppkpkmkl__activesessionview.html")
        
        if not windows:
            # looks for chrome-opened TabsOutliner window in tree
            windows = tree.find_instanced("crx_eggkanocgddhmamlbiijnphhppkpkmkl")

        return windows[0] if windows else False


    def _find_rover(self):
        tree = self.connection.get_tree()

        windows = tree.find_instanced("rover_panel")
        return windows[0] if windows else False


def pin(pinnable, workspace, left_margin, desired_width):
    pinnable.window.command("move container to workspace " + workspace.name + ", floating disable")

    # move window to left side

    pinnable.window.command("move position 6 27")
    pinnable.relocate()
    pinnable.window.command("move left")
    pinnable.relocate()

    # resize window to desired_width
    if (pinnable.window.rect.width > desired_width):
        delta = floor((pinnable.window.rect.width - desired_width) / 19.2)
        pinnable.window.command("resize shrink width {} px or {} ppt".format(delta, delta))
    elif (pinnable.window.rect.width < desired_width):
        delta = floor((desired_width - pinnable.window.rect.width) / 19.2)
        pinnable.window.command("resize grow width {} px or {} ppt".format(delta, delta))



if __name__ == "__main__":
    toggle_pin()
