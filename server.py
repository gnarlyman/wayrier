import os

import evdev
import ecodes
import asyncio
import sys
import pyclip
import ssl
import argparse


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
        self.clipboard_queue = asyncio.Queue()
        self.key_shift = False
        self.key_ctrl = False
        self.key_c = False

    async def queue_clipboard(self):
        await asyncio.sleep(1)
        value = pyclip.paste()
        print(f"copied {len(value)} bytes")
        await self.clipboard_queue.put(value)

    async def read_device(self, dev, dev_type):
        async for ev in dev.async_read_loop():
            if dev_type == 0:
                if ev.type == 1:
                    key = ecodes.bytype[ev.type][ev.code]
                    if key == 'KEY_SCROLLLOCK' and ev.value == 1:
                        if not self.grabbed:
                            dev.grab()
                            self.grabbed.enabled = True
                        else:
                            dev.ungrab()
                            self.grabbed.enabled = False
                    elif key == 'KEY_LEFTCTRL':
                        self.key_ctrl = ev.value in (1, 2)
                    elif key == 'KEY_C':
                        self.key_c = ev.value in (1, 2)

                    if not self.grabbed and self.key_c and self.key_ctrl:
                        asyncio.create_task(self.queue_clipboard())

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

    async def input_writer(self, reader, writer):
        while True:
            dev_type, code, ev_type, value = await self.queue.get()
            if self.grabbed:
                writer.write(f"{dev_type} {code} {ev_type} {value}\n".encode())

    async def clipboard_writer(self, reader, writer):
        while True:
            value = await self.clipboard_queue.get()
            writer.write(f"clipboard {len(value)}\n".encode())
            writer.write(value)

    async def server_callback(self, reader, writer):
        print("client connected")
        input_writer = asyncio.create_task(self.input_writer(reader, writer))
        clipboard_writer = asyncio.create_task(self.clipboard_writer(reader, writer))

        while True:
            if reader.at_eof():
                print("client disconnected")
                break
            await asyncio.sleep(1)

        input_writer.cancel()
        clipboard_writer.cancel()


async def main(port, disable_ssl=False):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    found_devices = [dev for dev in devices if 'Logitech' in dev.name]

    print(found_devices)

    inpt = InputHandler()
    for d in found_devices:
        caps = d.capabilities()
        dev_buttons = caps[1]

        if 1 in dev_buttons:
            asyncio.create_task(inpt.read_device(d, 0))
        else:
            asyncio.create_task(inpt.read_device(d, 1))

    ssl_ctx = None
    if not disable_ssl:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(f"{os.environ['HOME']}/certs/server.full.pem")
        ssl_ctx.load_verify_locations(cafile=f"{os.environ['HOME']}/certs/ca.pem")
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.VerifyMode.CERT_REQUIRED

    server = await asyncio.start_server(inpt.server_callback, '0.0.0.0', port, ssl=ssl_ctx)

    async with server:
        await server.serve_forever()


def get_args():
    parser = argparse.ArgumentParser(description="wayrier server")
    parser.add_argument(
        '--no-ssl', action='store_true',
        help='disable ssl (for testing, not recommended for real use)',
    )
    parser.add_argument(
        '--port', help='port to listen on',
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    asyncio.run(main(args.port, disable_ssl=args.no_ssl))
