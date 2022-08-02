import evdev
import asyncio
from selectors import DefaultSelector, EVENT_READ


class Grabbed:
    def __init__(self):
        self.enabled = False

    def __bool__(self):
        return self.enabled


class InputHandler:

    def __init__(self):
        self.grabbed = Grabbed()
        self.mouse_grabbed = False
        self.queue = asyncio.Queue()

    async def read_device(self, dev, dev_type):
        async for ev in dev.async_read_loop():
            if dev_type == 0:
                if ev.type == 1:
                    if ev.code == 70 and ev.value == 1:
                        if not self.grabbed:
                            dev.grab()
                            self.grabbed.enabled = True
                        else:
                            dev.ungrab()
                            self.grabbed.enabled = False

            elif dev_type == 1:
                if self.grabbed:
                    if not self.mouse_grabbed:
                        dev.grab()
                        self.mouse_grabbed = True
                else:
                    if self.mouse_grabbed:
                        dev.ungrab()
                        self.mouse_grabbed = False

            await self.queue.put((dev_type, ev.code, ev.type, ev.value))

    async def server_callback(self, reader, writer):
        print("client connected")
        while True:
            dev_type, code, ev_type, value = await self.queue.get()
            if self.grabbed:
                writer.write(f"{dev_type} {code} {ev_type} {value}\n".encode())


async def main():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    found_devices = [dev for dev in devices if 'Logitech' in dev.name]

    print(found_devices)

    inpt = InputHandler()
    for d in found_devices:
        caps = d.capabilities()
        dev_buttons = caps[1]

        if 1 in dev_buttons:
            asyncio.ensure_future(inpt.read_device(d, 0))
        else:
            asyncio.ensure_future(inpt.read_device(d, 1))

    server = await asyncio.start_server(inpt.server_callback, '0.0.0.0', 5842)

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
