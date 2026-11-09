"""
Official MMS (mackorone/mms) Python API Interface.
Communicates with the simulator via stdin/stdout.
"""

import sys


class MouseCrashedError(Exception):
    pass


def command(args, return_type=None):
    line = " ".join([str(x) for x in args]) + "\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    if return_type is not None:
        response = sys.stdin.readline()
        if not response:
            return None
        response = response.strip()
        if return_type == bool:
            return response == "true"
        return return_type(response)


def mazeWidth():
    return command(args=["mazeWidth"], return_type=int)


def mazeHeight():
    return command(args=["mazeHeight"], return_type=int)


def checkWall(wall_command, half_steps_away=None):
    args = [wall_command]
    if half_steps_away is not None:
        args.append(half_steps_away)
    return command(args=args, return_type=bool)


def wallFront(half_steps_away=None):
    return checkWall("wallFront", half_steps_away)


def wallRight(half_steps_away=None):
    return checkWall("wallRight", half_steps_away)


def wallLeft(half_steps_away=None):
    return checkWall("wallLeft", half_steps_away)


def wallBack(half_steps_away=None):
    return checkWall("wallBack", half_steps_away)


def moveForward(distance=None):
    args = ["moveForward"]
    if distance is not None:
        args.append(distance)
    response = command(args=args, return_type=str)
    if response == "crash":
        raise MouseCrashedError("Mouse crashed!")
    return response


def moveForwardHalf(num_half_steps=None):
    args = ["moveForwardHalf"]
    if num_half_steps is not None:
        args.append(num_half_steps)
    response = command(args=args, return_type=str)
    if response == "crash":
        raise MouseCrashedError("Mouse crashed!")
    return response


def turnRight():
    return command(args=["turnRight"], return_type=str)


def turnLeft():
    return command(args=["turnLeft"], return_type=str)


def turnRight45():
    return command(args=["turnRight45"], return_type=str)


def turnLeft45():
    return command(args=["turnLeft45"], return_type=str)


def setWall(x, y, direction):
    command(args=["setWall", x, y, str(direction).lower()])


def clearWall(x, y, direction):
    command(args=["clearWall", x, y, str(direction).lower()])


def setColor(x, y, color):
    command(args=["setColor", x, y, color])


def clearColor(x, y):
    command(args=["clearColor", x, y])


def clearAllColor():
    command(args=["clearAllColor"])


def setText(x, y, text):
    command(args=["setText", x, y, text])


def clearText(x, y):
    command(args=["clearText", x, y])


def clearAllText():
    command(args=["clearAllText"])


def wasReset():
    return command(args=["wasReset"], return_type=bool)


def ackReset():
    return command(args=["ackReset"], return_type=str)


def getStat(stat):
    return command(args=["getStat", stat], return_type=str)
