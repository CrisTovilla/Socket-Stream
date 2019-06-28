import socket
import sys
import cv2
import pickle
import struct
from data import DataSerializer

cam = cv2.VideoCapture(1)
cam.set(3, 320)
cam.set(4, 240)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.3.245"
    port = 8888
    print("connecting to: ", host, " | ", port)	

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    #message = input(" -> ")
    message = "Aveno estuvo tuvo tu tu aqui"

    while message != 'quit':
        ret, frame = cam.read()
        result, frame = cv2.imencode('.jpg', frame, encode_param)
    #    data = zlib.compress(pickle.dumps(frame, 0))
        ''' Se crea un data serializer con el frame y un mensaje '''
        send_data = DataSerializer(frame, "Saludos del cliente")
        data = pickle.dumps(send_data, 0)
        size = len(data)
        soc.sendall(struct.pack(">L", size) + data)
        # if soc.recv(5120).decode("utf8") == "-":
        #     print("Recibi2")
        #     pass        # null operation
        data = b""
        payload_size = struct.calcsize(">L")
        while len(data) < payload_size:
            print('a')
            data += soc.recv(4096)
    
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(data) < msg_size:
            print("Segundo while")
            data += soc.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        recv_data=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        print(recv_data.msg)
        frame = recv_data.frame
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow('ImageWindow',frame)
        cv2.waitKey(1)

        #message = input(" -> ")
    message = "Aveno estuvo tuvo tsu tu aqui"

    soc.send(b'--quit--')

if __name__ == "__main__":
	main()