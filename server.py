# server.py
import socket
import argparse
# from try123 import CANFDMessage
from PythonCAN import *
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
            message_code = 2    # 发送单帧CAN
            logger.info("once")
        else:
            message_code = 3    # 循环发送
            logger.info("cycle")

    else:
        if mes.lower() == 'stop':
            message_code = 4    # 停发
        elif mes.lower().startswith('connect'):
            message_code = 1    # 连接
        elif mes.lower() == 'disconnect':
            message_code = 5    # 断接
        elif mes.lower() == 'quit':
            message_code = 6    # 连接


    logger.info(f"get message_code = {message_code}")
    return message_code


shutdown_flag = False
def start_server(host, port):
    global shutdown_flag
    # 创建一个TCP/IP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定套接字到指定的地址和端口
    server_socket.bind((host, port))

    # 监听传入连接
    server_socket.listen(1)
    print(f"Server started on {host}:{port}. Waiting for a connection...")

    try:
        while not shutdown_flag:
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

                    # assert message == "CAN1,500k,1000ms,592,02 01 00 0E 00 00 00 00"

                    message_code = message_classify(message)
                    # tscan_class_msg = CANMessage(message).get_message()
                    match message_code:
                        case 1:
                            connect()
                        case 2:
                            tscan_class_msg = CANMessage(message).get_message()
                            send_can_message_once(tscan_class_msg)

                        case 3:
                            tscan_class_msg = CANMessage(message).get_message()
                            send_can_Message_with_msg(tscan_class_msg)

                        case 4:
                            # tscan_class_msg = CANMessage(message).get_message()

                            stop_cyclic_msg_CAN(tscan_class_msg)
                        case 5:
                            tsapp_disconnect()
                        case 6:
                            shutdown_flag = True
                            break
                        case 7:
                            pass
                        case 8:
                            pass
                        case _:
                            print("double check your command")

            except Exception as e:
                logger.exception(f"error occurs： {e}\n")
                continue
            finally:
                # 关闭连接
                client_socket.close()
                logger.info("Connection closed.")
                if shutdown_flag:
                    break
    except KeyboardInterrupt:
        logger.info("\nServer shutting down.")
    finally:
        logger.info("Server closed.")
        server_socket.close()








if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple TCP Server")
    parser.add_argument('--host', default='127.0.0.1', help='Host address to bind (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=65432, help='Port to listen on (default: 65432)')
    args = parser.parse_args()

    start_server(args.host, args.port)
    os._exit(0)