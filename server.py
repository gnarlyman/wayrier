import evdev
import asyncio


class Grabbed:
    def __init__(self):
        self.enabled = False

    def __bool__(self):
        return self.enabled


class InputHandler:
    dev = None
    dev_type = None

    def __init__(self, dev, dev_type, grabbed):
        self.dev = dev
        self.dev_type = dev_type
        self.grabbed = grabbed
        self.mouse_grabbed = False

    async def read_keyboard(self):
        async for ev in self.dev.async_read_loop():
            if ev.type == 1:
                if ev.code == 70 and ev.value == 1:
                    if not self.grabbed:
                        self.dev.grab()
                        self.grabbed.enabled = True
                    else:
                        self.dev.ungrab()
                        self.grabbed.enabled = False

                yield ev.code, ev.type, ev.value

    async def read_mouse(self):
        async for ev in self.dev.async_read_loop():
            if self.grabbed:
                if not self.mouse_grabbed:
                    self.dev.grab()
                    self.mouse_grabbed = True
            else:
                if self.mouse_grabbed:
                    self.dev.ungrab()
                    self.mouse_grabbed = False

            yield ev.code, ev.type, ev.value

    async def server_callback(self, reader, writer):
        print("client connected")
        writer.write(f"{self.dev_type}\n".encode())
        if self.dev_type == "keyboard":
            async for code, ev_type, value in self.read_keyboard():
                if self.grabbed:
                    writer.write(f"{code} {ev_type} {value}\n".encode())

        elif self.dev_type == "mouse":
            async for code, ev_type, value in self.read_mouse():
                if self.grabbed:
                    writer.write(f"{code} {ev_type} {value}\n".encode())


def main():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    found_devices = [dev for dev in devices if 'Logitech' in dev.name]

    print(found_devices)

    loop = asyncio.get_event_loop()

    grabbed = Grabbed()

    for dev in found_devices:
        caps = dev.capabilities()
        dev_buttons = caps[1]

        # if it has the escape key, it's a keyboard
        if 1 in dev_buttons:
            asyncio.ensure_future(
                asyncio.start_server(
                    InputHandler(dev, "keyboard", grabbed).server_callback, '0.0.0.0', 5842, loop=loop
                )
            )
        else:
            asyncio.ensure_future(
                asyncio.start_server(
                    InputHandler(dev, "mouse", grabbed).server_callback, '0.0.0.0', 5843, loop=loop
                )
            )

    loop.run_forever()


if __name__ == '__main__':
    main()
