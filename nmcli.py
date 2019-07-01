import sys
import zmq

target = "openbts"
command = "config"
action = "read"
key = "GSM.Radio.SNRTarget"
value = ""

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:45060")



request = '{"command":"' + command + '","action":"' + action + '","key":"' + key + '","value":"' + value + '"}'

print ("raw request: " + request)
socket.send_string(request)
response = socket.recv()

print (response.decode('utf-8'))

