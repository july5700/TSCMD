import socket
import argparse
from loguru import logger


def send_message(host, port, messages):
    # 创建一个TCP/IP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接到服务器
        client_socket.connect((host, port))
        logger.info(f"Connected to {host}:{port}")

        # 发送所有消息，以换行符分隔
        full_message = ' '.join(messages)
        client_socket.sendall(full_message.encode('utf-8'))
        logger.info(f"Sent messages: {full_message}")
    finally:
        # 关闭连接
        client_socket.close()
        logger.info("Connection closed.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple TCP Client")
    parser.add_argument('--host', default='127.0.0.1', help='Host address to connect to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=65432, help='Port to connect on (default: 65432)')
    parser.add_argument('--messages', nargs='+', help='Messages to send to the server')
    args = parser.parse_args()

    send_message(args.host, args.port, args.messages)