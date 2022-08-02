from pynput.mouse import Button, Controller as mC
from pynput.keyboard import Key, Controller as kC
import sys
import asyncio
import ecodes

keymap = {
    "KEY_0": '0',
    "KEY_1": '1',
    "KEY_2": '2',
    "KEY_3": '3',
    "KEY_4": '4',
    "KEY_5": '5',
    "KEY_6": '6',
    "KEY_7": '7',
    "KEY_8": '8',
    "KEY_9": '9',
    "KEY_A": 'a',
    "KEY_B": 'b',
    "KEY_C": 'c',
    "KEY_D": 'd',
    "KEY_E": 'e',
    "KEY_F": 'f',
    "KEY_G": 'g',
    "KEY_H": 'h',
    "KEY_I": 'i',
    "KEY_J": 'j',
    "KEY_K": 'k',
    "KEY_L": 'l',
    "KEY_M": 'm',
    "KEY_N": 'n',
    "KEY_O": 'o',
    "KEY_P": 'p',
    "KEY_Q": 'q',
    "KEY_R": 'r',
    "KEY_S": 's',
    "KEY_T": 't',
    "KEY_U": 'u',
    "KEY_V": 'v',
    "KEY_W": 'w',
    "KEY_X": 'x',
    "KEY_Y": 'y',
    "KEY_Z": 'z',
    "KEY_LEFTSHIFT": Key.shift,
    "KEY_LEFTCTRL": Key.ctrl,
    "KEY_LEFTMETA": Key.cmd,
    "KEY_SPACE": Key.space,
    "KEY_LEFTALT": Key.alt,
    "KEY_TAB": Key.tab,
    "KEY_BACKSPACE": Key.backspace,
    "KEY_ENTER": Key.enter,
    "KEY_ESC": Key.esc,
    "KEY_DELETE": Key.delete,
    "KEY_UP": Key.up,
    "KEY_DOWN": Key.down,
    "KEY_LEFT": Key.left,
    "KEY_RIGHT": Key.right,
    "KEY_MINUS": '-',
    "KEY_EQUAL": '=',
    "KEY_GRAVE": '`',
    "KEY_SEMICOLON": ';',
    "KEY_SLASH": '/',
    "KEY_BACKSLASH": '\\',
    "KEY_LEFTBRACE": '[',
    "KEY_RIGHTBRACE": ']',
    "KEY_COMMA": ',',
    "KEY_DOT": '.',
}

keyboard = kC()
mouse = mC()


async def keyboard_client(code, ev_type, value):
    key = ecodes.KEY[code]
    if key not in keymap:
        return

    elif value == 1:
        keyboard.press(keymap[key])
    elif value == 0:
        keyboard.release(keymap[key])


async def mouse_client(code, ev_type, value):
    if code == 0:
        mouse.move(value, 0)
    elif code == 1:
        mouse.move(0, value)
    elif code == 272 and value == 1:
        mouse.press(Button.left)
    elif code == 272 and value == 0:
        mouse.release(Button.left)
    elif code == 273 and value == 1:
        mouse.press(Button.right)
    elif code == 273 and value == 0:
        mouse.release(Button.right)
    elif code == 274 and value == 1:
        mouse.press(Button.middle)
    elif code == 274 and value == 0:
        mouse.release(Button.middle)
    elif code == 8 and value == 1:
        mouse.scroll(0, 10)
    elif code == 8 and value == -1:
        mouse.scroll(0, -10)


async def start():
    host, port = sys.argv[1], sys.argv[2]
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            print(f"connected to {host}:{port}")
            while True:
                data = await reader.readline()
                device_type, code, ev_type, value = map(int, data.decode().split())
                if device_type == 0:
                    await keyboard_client(code, ev_type, value)
                elif device_type == 1:
                    await mouse_client(code, ev_type, value)
                else:
                    print('unknown device or bad line')

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)

        await asyncio.sleep(1)


def main():
    asyncio.run(start())


if __name__ == '__main__':
    main()
