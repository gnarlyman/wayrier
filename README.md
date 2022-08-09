# Wayrier
A basic tool for sharing wayland mouse and keyboard to other systems

Server only works on linux with evdev.  
Clients should work on X11 linux, Mac, and Windows with pynput. 

Switches keyboard and mouse input to connected client. Server mouse/keyboard input is disabled while switched.

Switching key:
Scroll lock

Known limitations:
- Double-click does not work on mac with pynput. A workaround has been implemented, use mouse-4 to double-click.
- In wayland, periodically checking paste buffer for changes causes undesirable behavior 
Workaround is to detect ctrl+c keypress and only capture clipboard then.
- Can't be run as a service on server due to clipboard integration. On mac as well due to pynput.

TODO:
- Add encryption and client validation
- client > server clipboard
- better clipboard management
- make switching-key configurable
- optional/configurable visual indication of current controlled screen
- better detection and handling of input devices on server

WIP

## openssl commands

- extra attributes for server cert (filename: domain.ext)
```
subjectAltName = @alt_names
[alt_names]
DNS.1 = <server-hostname>
IP.1 = <server ip>
```

- Generate a Certificate Authority key 
```
openssl genrsa -out ca.key 2048
openssl req -x509 -sha256 -new -nodes -key ca.key -days 3650 -out ca.pem
```
- Create client key and certificate signed by CA
```
CLIENT_ID="client"
CLIENT_SERIAL=01
openssl genrsa -out ${CLIENT_ID}.key 2048
openssl req -new -key ${CLIENT_ID}.key -out ${CLIENT_ID}.csr
openssl x509 -req -days 3650 -in ${CLIENT_ID}.csr -CA ca.pem -CAkey ca.key -set_serial ${CLIENT_SERIAL} -out ${CLIENT_ID}.pem
cat ${CLIENT_ID}.key ${CLIENT_ID}.pem ca.pem > ${CLIENT_ID}.full.pem
openssl pkcs12 -export -out ${CLIENT_ID}.full.pfx -inkey ${CLIENT_ID}.key -in ${CLIENT_ID}.pem -certfile ca.pem
```
- Create a server key and certificate signed by CA
```
SERVER_ID="server"
SERVER_SERIAL=02
openssl genrsa -out ${SERVER_ID}.key 2048
openssl req -new -key ${SERVER_ID}.key -out ${SERVER_ID}.csr
openssl x509 -req -days 3650 -in ${SERVER_ID}.csr -CA ca.pem -CAkey ca.key -set_serial ${SERVER_SERIAL} -out ${SERVER_ID}.pem -extfile domain.ext
cat ${SERVER_ID}.key ${SERVER_ID}.pem ca.pem > ${SERVER_ID}.full.pem
```
