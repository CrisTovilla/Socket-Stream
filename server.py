import socket
import sys
import traceback
import cv2
from threading import Thread
import pickle
from data import DataSerializer
import struct ## new


encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]


def main():
    start_server()


def start_server():
    host = "192.168.3.245"
    port = 8888         # arbitrary non-privileged port

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(5)       # queue up to 5 requests
    print("Socket now listening")

    # infinite loop- do not reset for every requests
    while True:
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()

    soc.close()


def client_thread(connection, ip, port, max_buffer_size = 4096):
    is_active = True

 
    while is_active:
        client_input = receive_input(connection, max_buffer_size)

        if "--QUIT--" in client_input:
            print("Client is requesting to quit")
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            is_active = False
        else:
            image= cv2.cvtColor(client_input,cv2.COLOR_BGR2GRAY)
            result, frame = cv2.imencode('.jpg', image, encode_param)
            ''' Creating a SerializerData that includes a message and frame '''
            send_data = DataSerializer(frame, "Saludos del server")
            data = pickle.dumps(send_data, 0)
            size = len(data)

            connection.sendall(struct.pack(">L", size) + data)


def receive_input(connection, max_buffer_size):
    data = b""
    payload_size = struct.calcsize(">L")
    temp = len(data)
    disconnected_socket = False
    while len(data) < payload_size:
        print("Primer while, Recv: {}".format(len(data)))
        data += connection.recv(4096)
        if temp == len(data):
            disconnected_socket = True
            break
        temp = len(data)

    if not disconnected_socket:        
        print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            print("Segundo while")
            data += connection.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        recv_data = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = recv_data.frame
        print(recv_data.msg)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        result = process_input(frame)

        return frame 
    else:
        return ['--QUIT--']


def process_input(input_str):
    print("Processing the input received from client")

    return "Hello " + str(input_str).upper()

if __name__ == "__main__":
    main()