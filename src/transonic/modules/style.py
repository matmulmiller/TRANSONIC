colors = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    'bright_yellow': '\033[93m'
} 

symbols = {
    "spade": '\u2660'
}

titles = {
    "classic":  f"{colors.get("cyan")}  _____ ___    _   _  _ ___  ___  _  _ ___ ___ \n |_   _| _ \\  /_\\ | \\| / __|/ _ \\| \\| |_ _/ __|\n   | | |   / / _ \\| .` \\__ \\ (_) | .` || | (__ \n   |_| |_|_\\/_/ \\_\\_|\\_|___/\\___/|_|\\_|___\\___|\n                                               \n{colors.get("green")}",
    "shifted": f"{colors.get("cyan")} _________  ___   _  __________  _  ___________\n/_  __/ _ \\/ _ | / |/ / __/ __ \\/ |/ /  _/ ___/\n / / / , _/ __ |/    /\\ \\/ /_/ /    // // /__  \n/_/ /_/|_/_/ |_/_/|_/___/\\____/_/|_/___/\\___/  \n                                               \n{colors.get("green")}",
    "minimal": f"{colors.get("cyan")}\nTRANSONIC\n{colors.get("green")}",
    "galactic": f"{colors.get("yellow")}.___________..______          ___      .__   __.      _______.  ______   .__   __.  __    ______ \n|           ||   _  \\        /   \\     |  \\ |  |     /       | /  __  \\  |  \\ |  | |  |  /      |\n`---|  |----`|  |_)  |      /  ^  \\    |   \\|  |    |   (----`|  |  |  | |   \\|  | |  | |  ,----'\n    |  |     |      /      /  /_\\  \\   |  . `  |     \\   \\    |  |  |  | |  . `  | |  | |  |     \n    |  |     |  |\\  \\----./  _____  \\  |  |\\   | .----)   |   |  `--'  | |  |\\   | |  | |  `----.\n    |__|     | _| `._____/__/     \\__\\ |__| \\__| |_______/     \\______/  |__| \\__| |__|  \\______|\n                                                                                                 {colors.get("bright_yellow")}"
}
