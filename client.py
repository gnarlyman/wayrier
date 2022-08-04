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


class Control:
    def __init__(self):
        self.x, self.y = 0, 0

    async def keyboard_client(self, code, ev_type, value):
        key = ecodes.KEY[code]
        if key not in keymap:
            return

        elif value == 1 or value == 2:
            keyboard.press(keymap[key])
        elif value == 0:
            keyboard.release(keymap[key])

    async def mouse_client(self, code, ev_type, value):
        m = ecodes.bytype[ev_type][code]
        if m == 'SYN_REPORT':
            mouse.move(self.x, self.y)
            self.x, self.y = 0, 0
        elif m == 'REL_X':
            self.x += value
        elif m == 'REL_Y':
            self.y += value
        elif 'BTN_LEFT' in m and value == 1:
            mouse.press(Button.left)
        elif 'BTN_LEFT' in m and value == 0:
            mouse.release(Button.left)
        elif 'BTN_RIGHT' in m and value == 1:
            mouse.press(Button.right)
        elif 'BTN_RIGHT' in m and value == 0:
            mouse.release(Button.right)
        elif 'BTN_MIDDLE' in m and value == 1:
            mouse.press(Button.middle)
        elif 'BTN_MIDDLE' in m and value == 0:
            mouse.release(Button.middle)
        elif 'REL_WHEEL' in m and value == 1:
            mouse.scroll(0, 10)
        elif 'REL_WHEEL' in m and value == -1:
            mouse.scroll(0, -10)


async def start():
    c = Control()

    host, port = sys.argv[1], sys.argv[2]
    reader, writer = None, None
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            print(f"connected to {host}:{port}")
            while True:
                if reader.at_eof():
                    break

                data = await reader.readline()
                if not data.strip():
                    break

                device_type, code, ev_type, value = map(int, data.decode().split())
                if device_type == 0:
                    await c.keyboard_client(code, ev_type, value)
                elif device_type == 1:
                    await c.mouse_client(code, ev_type, value)
                else:
                    print('unknown device or bad line')

            writer.close()
            await writer.wait_closed()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error", e)
        finally:
            writer.close()
            await writer.wait_closed()

        await asyncio.sleep(1)


def main():
    asyncio.run(start())


if __name__ == '__main__':
    main()
