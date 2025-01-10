# server.py
import socket
import argparse
# from try123 import CANFDMessage
from PythonCANFD import *
from loguru import logger

import os
"""
Todo:
1. 给message做分类，以空格为间隔
2. 甄别message类别，需要从FTimeUs判断是循环发，还是发单帧
"""


mes = "CAN1,500k,0ms,592,02 01 00 0E 00 00 00 00"
mes = "q"

def message_classify(mes):
    message_code = 0
    mes_list = mes.split(',')
    if len(mes_list) == 5:
        logger.info(mes_list)
        if mes_list[2].lower() == '0ms':
            message_code = 4    # 发送单帧CAN
            print("once")
        else:
            message_code = 1    # 循环发送
            print("cycle")

    else:
        if mes.lower() == 'q':
            message_code = 2    # 关闭
        elif mes.lower().startswith('connect'):
            message_code = 3    # 连接

    logger.info(f"get message_code = {message_code}")
    return message_code

# if __name__ == '__main__':
#     print("hi")
#     print(message_classify(mes))
#
# os._exit(0)



def start_server(host, port):
    # 创建一个TCP/IP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定套接字到指定的地址和端口
    server_socket.bind((host, port))

    # 监听传入连接
    server_socket.listen(1)
    print(f"Server started on {host}:{port}. Waiting for a connection...")

    try:
        while True:
            # 等待客户端连接
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            try:
                while True:
                    # 接收数据
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    print(f"Received message: {message}")
                    print("assert start")
                    # assert message == "CAN1,500k,1000ms,592,02 01 00 0E 00 00 00 00"
                    print("assert over")
                    message_code = message_classify(message)
                    # tscan_class_msg =
                    match message_code:
                        case 1:
                            tscan_class_msg = CANMessage(message).get_message()
                            send_can_Message_with_msg(tscan_class_msg)
                        case 3:
                            print("gonna connect")
                            connect()
                        case _:
                            print("Todo")

            except Exception as e:
                print(f"e is {e}")
            # finally:
            #     # 关闭连接
            #     client_socket.close()
            #     print("Connection closed.")
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()








if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple TCP Server")
    parser.add_argument('--host', default='127.0.0.1', help='Host address to bind (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=65432, help='Port to listen on (default: 65432)')
    args = parser.parse_args()

    start_server(args.host, args.port)