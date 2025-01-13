# Python实现CANFD报文的收发
from TSMasterAPI import *
from ctypes import *
import tkinter as tk
from tkinter import filedialog
from loguru import logger


from TSMasterAPI.TSEnum import _TLIBApplicationChannelType, _TLIBBusToolDeviceType, _TLIB_TS_Device_Sub_Type, \
    _TLIBCANFDControllerType, _TLIBCANFDControllerMode, _TSupportedObjType

AppName = b'20240409PythonCANFD'


# CANFD报文定义
CANFD_Msg = TLIBCANFD()
CANFD_Msg.FIdxChn = 1
CANFD_Msg.FDLC = 8
CANFD_Msg.FIdentifier = 0x591
CANFD_Msg.FFDProperties = 3
CANFD_Msg.FTimeUs = 100
# FData = [0x0A,0x55,0x98,0,0,0,0,0]
FData = [0x02,0x00,0x00,0xFF,0,0,0,0]
for i in range(len(FData)):
    CANFD_Msg.FData[i] = FData[i]


# CANFD_Msg = TLIBCANFD()
# CANFD_Msg.FIdxChn = 1
# CANFD_Msg.FDLC = 15
# CANFD_Msg.FIdentifier = 0x53
# CANFD_Msg.FFDProperties = 30
# CANFD_Msg.FTimeUs = 10
# FData = [0x3F,0x40,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
# for i in range(len(FData)):
#     CANFD_Msg.FData[i] = FData[i]

# def get_can_msg()
# CAN报文定义
CAN_Msg = TLIBCAN()
CAN_Msg.FIdxChn = 1
CAN_Msg.FDLC = 8
CAN_Msg.FIdentifier = 0x591
CAN_Msg.FProperties = 0
CAN_Msg.FTimeUs = 50000000
# FData1 = [0x25, 0x87, 0x14, 0x01, 0x30, 0x0, 0x0, 0x0]
FData1 = [0x02,0x00,0x00,0xFF,0,0,0,0]
# logger.info(f"FData1 data type = {type(FData1[0])}")
for i in range(len(FData1)):
    CAN_Msg.FData[i] = FData1[i]


class CANMessage:
    def __init__(self, params):
        """
        初始化 CANMessage 实例，并根据提供的参数设置属性。

        :param params: 一个包含配置信息的字符串，格式为 "CAN8,500k,1000ms,591,02 01 00 0E 00 00 00 00"
        """
        self.CAN_Msg = TLIBCAN()
        self.parse_params(params)

    def parse_params(self, params):
        """
        解析参数字符串，并设置 CANFD_Msg 的相应属性。

        :param params: 参数字符串
        """
        # 分割参数字符串
        parts = params.split(',')
        if len(parts) != 5:
            raise ValueError("参数格式不正确，应该有五个部分")

        # 设置通道索引（FIdxChn）
        try:
            self.CAN_Msg.FIdxChn = int(parts[0][3:])  # 假设格式总是 "CANx"
        except ValueError:
            raise ValueError("无效的通道索引")

        # 设置时间戳（FTimeUs），单位为微秒
        try:
            time_us = parts[2].replace('ms', '')
            self.CAN_Msg.FTimeUs = int(time_us) * 1000  # 将毫秒转换为微秒
        except ValueError:
            raise ValueError("无效的时间戳")

        # 设置标识符（FIdentifier）
        try:
            self.CAN_Msg.FIdentifier = int(parts[3], 16)
        except ValueError:
            raise ValueError("无效的标识符")

        # 设置数据字段（FData）
        data_parts = parts[4].split()
        if len(data_parts) > 8:
            raise ValueError("数据长度超过8字节")
        FData = [int(d, 16) for d in data_parts]
        self.CAN_Msg.FDLC = len(FData)  # 设置数据长度码
        for i in range(len(FData)):
            self.CAN_Msg.FData[i] = FData[i]
        # logger.info(f"type of FData = {type(FData[0])}")

        # 设置默认值
        self.CAN_Msg.FProperties = 0  # 根据需要调整

    def get_message(self):
        """返回配置好的 TLIBCANFD 对象"""
        return self.CAN_Msg



# os._exit(0)
count1 = 0

def on_can_event(OBJ, ACAN):
    global count1
    if(ACAN.contents.FIdentifier == 0x10 and ACAN.contents.FIdxChn == 0):
        # ACAN.contents.FData[0] += 1
        tsapp_transmit_can_async(CAN_Msg)
    if(ACAN.contents.FIdentifier == 0x111 and ACAN.contents.FIdxChn == 1):
        count1 += 1
        logger.info(ACAN.contents.FData)

obj = c_int32(0)
id1 = c_ulong(0)    # 加载dbc句柄
OnCanEvent = TCANQueueEvent_Win32(on_can_event)


def connect():
    # 直接打开同星的工程，这样就无需配置了
    # initialize_lib_tsmaster_with_project(APPName, b'D:\\Desktop\\test')
    # 初始化函数，所需所有函数调用的接口
    initialize_lib_tsmaster(AppName)

    # 设置CAN通道数
    if tsapp_set_can_channel_count(2) == 0:
        logger.info("CAN通道设置成功")
    else:
        logger.info("CAN通道设置失败", tsapp_set_can_channel_count(2))

    # 设置LIN通道数
    if tsapp_set_lin_channel_count(0) == 0:
        logger.info("LIN通道设置成功")
    else:
        logger.info("LIN通道设置失败", tsapp_set_lin_channel_count(0))

    # 通道映射至软件通道
    # TOSUN其他硬件对应第6个参数，找到对应型号即可
    if 0 == tsapp_set_mapping_verbose(AppName,
                                      _TLIBApplicationChannelType.APP_CAN,
                                      0,    # CHANNEL_INDEX.CHN1,
                                      "TC1034".encode("utf8"),
                                      _TLIBBusToolDeviceType.TS_USB_DEVICE,
                                      _TLIB_TS_Device_Sub_Type.TC1034,
                                      0,    # 硬件序号
                                      0,    # 硬件通道
                                      True):
        logger.info("1通道映射成功")
    else:
        logger.info("1通道映射失败")

    if 0 == tsapp_set_mapping_verbose(AppName,
                                      _TLIBApplicationChannelType.APP_CAN,
                                      1,    # CHANNEL_INDEX.CHN2,
                                      "TC1034".encode("utf8"),
                                      _TLIBBusToolDeviceType.TS_USB_DEVICE,
                                      _TLIB_TS_Device_Sub_Type.TC1034,
                                      0,
                                      1,
                                      True):
        logger.info("2通道映射成功")
    else:
        logger.info("2通道映射失败")

    # 设置CANFD的波特率
    if 0 == tsapp_configure_baudrate_canfd(0,       # CHANNEL_INDEX.CHN1,
                                           500.0,   # 仲裁段波特率
                                           2000.0,  # 数据段波特率
                                           _TLIBCANFDControllerType.lfdtISOCAN,
                                           _TLIBCANFDControllerMode.lfdmNormal,
                                           True):
        logger.info("1通道CANFD波特率成功")
    else:
        logger.info("1通道CANFD波特率失败")

    if 0 == tsapp_configure_baudrate_canfd(1,       # CHANNEL_INDEX.CHN2,
                                           500.0,
                                           2000.0,
                                           _TLIBCANFDControllerType.lfdtISOCAN,
                                           _TLIBCANFDControllerMode.lfdmNormal,
                                           True):
        logger.info("1通道CANFD波特率成功")
    else:
        logger.info("1通道CANFD波特率失败")

    # 注册回调事件
    if 0 == tsapp_register_pretx_event_can(obj, OnCanEvent):
        logger.info("回调事件注册成功")
    else:
        logger.info("回调事件注册失败")

    if 0 == tsapp_register_event_can(obj,OnCanEvent):
        logger.info("q")

    # 连接
    if 0 == tsapp_connect():    # 硬件0点
        logger.info("CAN工具连接成功")
        #硬件开启成功后，开启FIFO接收
        tsfifo_enable_receive_fifo()
    else:
        logger.info("CAN工具连接失败")




# CANFD发送报文
def send_canfd_Message():
    # for i in range(10):
    # 发一帧
    #     r = tsapp_transmit_canfd_async(CANFD_Msg)
    # if r == 0:
    #     logger.info("CANFD报文发送成功")
    # else:
    #     logger.info("CANFD报文发送you wenti")
    #     logger.info(r)

    # p = tsapp_add_cyclic_msg_canfd(CANFD_Msg,500)
    p = tsapp_add_cyclic_msg_can(CAN_Msg,500)

    if p == 0:
        logger.info("CAN周期发送成功")
        logger.info(f"CAN_Msg = {CAN_Msg}")
        logger.info(f"type of CAN_Msg = {type(CAN_Msg)}")

def send_can_Message_with_msg(CAN_Msg):
    # for i in range(10):
    # 发一帧
    #     r = tsapp_transmit_canfd_async(CANFD_Msg)
    # if r == 0:
    #     logger.info("CANFD报文发送成功")
    # else:
    #     logger.info("CANFD报文发送you wenti")
    #     logger.info(r)

    # p = tsapp_add_cyclic_msg_canfd(CANFD_Msg,500)
    p = tsapp_add_cyclic_msg_can(CAN_Msg,500)
    if p == 0:
        logger.info("CAN周期发送成功")
        logger.info(f"CAN_Msg = {CAN_Msg}")
        logger.info(f"type of CAN_Msg = {type(CAN_Msg)}")

def send_can_message_once(can_msg):
    p = tsapp_transmit_can_async(can_msg)
    if p == 0:
        logger.info("单帧CAN发送成功")
        logger.info(f"can_msg = {can_msg}")
        logger.info(f"type of can_msg = {type(can_msg)}")

# 删除所有循环发送的CANFD报文
def stop_cyclic_msg_CANFD():
    global CANFD_Msg
    tsapp_delete_cyclic_msg_canfd(CANFD_Msg)
    tsapp_delete_cyclic_msg_can(CAN_Msg)

def stop_cyclic_msg_CAN(CAN_Msg):
    global CANFD_Msg
    # tsapp_delete_cyclic_msg_canfd(CANFD_Msg)
    tsapp_delete_cyclic_msg_can(CAN_Msg)

def receive_can_message():
    ListCANMsg = (TLIBCAN*100)()        # CANFD接收报文数组
    CANSize = c_int32(100)                # CANFD接收报文数组大小


    # 执行该步骤之前需要提前开启fifo
    r = tsfifo_receive_can_msgs(ListCANMsg,                     # ACANFDBuffers ACAN 数组
                                  CANSize,                        # ACANFDBuffers ACAN 数组大小
                                  0 ,                               # AChn 通道编号
                                  0)    # ARxTx 是否收发报文
    logger.info("接收返回值：", r)                  # 返回值为0代表设置成功，非0失败，根据错误码查看错误类型

    logger.info("ACAN数据大小 = ",CANSize)
    for i in range(CANSize.value):
        logger.info("FIFO接收CANFD ID = ",ListCANMsg[i].FIdentifier)
        logger.info("ListCANFDMsg[%d].FData" % i)
        for d in range(ListCANMsg[i].FDLC):     #查看报文
            logger.info(ListCANMsg[i].FData[d],end=' ')
        logger.info("\n")



# 接收CANFD报文
def receive_canfd_message():
    ListCANFDMsg = (TLIBCANFD*100)()        # CANFD接收报文数组
    CANFDSize = c_int32(100)                # CANFD接收报文数组大小

    # 执行该步骤之前需要提前开启fifo
    r = tsfifo_receive_canfd_msgs(ListCANFDMsg,                     # ACANFDBuffers ACAN 数组
                                  CANFDSize,                        # ACANFDBuffers ACAN 数组大小
                                  0 ,                               # AChn 通道编号
                                  0)    # ARxTx 是否收发报文
    logger.info("接收返回值：", r)                  # 返回值为0代表设置成功，非0失败，根据错误码查看错误类型

    logger.info("ACAN数据大小 = ",CANFDSize)
    for i in range(CANFDSize.value):
        logger.info("FIFO接收CANFD ID = ",ListCANFDMsg[i].FIdentifier)
        logger.info("ListCANFDMsg[%d].FData" % i)
        for d in range(ListCANFDMsg[i].FDLC):     #查看报文
            logger.info(ListCANFDMsg[i].FData[d],end=' ')
        logger.info("\n")



# 加载dbc文件
def load_dbc():
    global id1
    root = tk.Tk()                              # 创建一个Tkinter窗口对象
    root.title("请选择dbc文件")
    root.withdraw()                             # 隐藏主窗口
    filepath = filedialog.askopenfilename()     # 打开文件选择对话框
    if str(filepath).find(".dbc") != -1:
        # 加载dbc并绑定通道
        r = tsdb_load_can_db(filepath.encode("utf8"), b"0,1", id1)  # dbc文件绝对路径；绑定的通道；dbc句柄
        if r == 0:
            logger.info("id1 = ", id1)
            logger.info(filepath[filepath.rindex("/") + 1:] + "文件加载成功")
        return filepath
    else:
        logger.info("文件不正确")
        return 0

# 卸载dbc文件
def unload_dbc():
    if 0 == tsdb_unload_can_dbs():
        logger.info("dbc文件全部卸载")


fileName_log = "C:\\Users\\tosun\\Desktop\\[2014 s t]\\TestData.blf".encode("utf-8")
# 录制报文
def start_logging():
    tsapp_start_logging(fileName_log)   # 开始录制报文（包含所有硬件的所有通道的所有报文，均存储在一个文件里）

# 停止录制
def stop_loggging():
    tsapp_stop_logging()    # 停止录制

udsHandle = c_long(0)

# 诊断服务
def create_uds_module():
    global udsHandle        # 诊断模块句柄
    supportFD = 0           # 支持CANFD
    MaxDLC = 8              # 最大DLC
    ReqId = 0x7C0           # 请求ID
    ReqIdIsStd = True       # 请求ID是否为标准数据帧
    ResId = 0x7C8           # 响应ID
    ResIdIsStd = True       # 响应ID是否为标准数据帧
    FctId = 0x7DF           # 功能ID
    FctIdIsStd = True       # 功能ID是否为标准数据帧
    # 创建诊断服务
    r = tsdiag_can_create(udsHandle,
                          0,
                          supportFD,
                          MaxDLC,
                          ReqId,
                          ReqIdIsStd,
                          ResId,
                          ResIdIsStd,
                          FctId,
                          FctIdIsStd)

    if r == 0:
        logger.info("UDS handle = ",udsHandle)
    else:
        logger.info(tsapp_get_error_description(r))   # 获取错误信息

# 请求并获取响应数据 requestID 发送
def req_and_res_can():
    global udsHandle                        # 诊断模块句柄
    AReqDataArray = (c_uint8 * 100)()       # 发送的数据数组
    AReqDataArray[0] = c_uint8(0x22)
    AReqDataArray[1] = c_uint8(0xf1)
    AReqDataArray[2] = c_uint8(0x90)
    AReqSize = 3                            # 发送的数据长度
    AResSize = c_int(100)                   # 回复的数据数组
    AResponseDataArray = (c_uint8 * 1000)() # 回复的数据长度

    # 请求并获取响应数据 requestID 发送
    r = tstp_can_request_and_get_response(udsHandle, AReqDataArray, AReqSize, AResponseDataArray, AResSize)
    logger.info("响应的数据长度：", AResSize)
    for i in range(AResSize.value):
        logger.info(hex(AResponseDataArray[i]),end="  ")
        if i == AResSize.value-1:
            logger.info(end="\n")

blfID = c_ulong(0)  # blf句柄
count = c_long(0)  # blf文件包含报文数

# 读取blf
def read_blf():
    global blfID, count
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename()
    # filepath = "C:/Users/tosun/Desktop/123456879.blf"
    if str(filepath).find(".blf") != -1:
        # 开始读取blf
        r = tslog_blf_read_start(filepath.encode('utf8'), blfID, count)
        if r == 0:
            logger.info(filepath[filepath.rindex("/") + 1:] + "文件加载成功")

# 读取blf文件数据
def read_blf_datas():
    global blfID, count
    realCount = c_long(0)                      # 读取的报文指针
    messageType = c_long(_TSupportedObjType.sotUnknown.value)   # 当前报文类型

    CANTemp = TLIBCAN()                         # CAN报文数据
    CANFDTemp = TLIBCANFD()                     # CANFD报文数据
    LINTemp = TLIBLIN()                         # LIN报文数据

    for i in range(count.value):
        # 读当前报文的类型，并赋值给报文指针
        tslog_blf_read_object(blfID, realCount, messageType, CANTemp, LINTemp, CANFDTemp)    # 读当前报文的类型，并赋值给报文指针
        if messageType.value == (c_long(_TSupportedObjType.sotCAN.value)).value:
            logger.info(CANTemp.FTimeUs / 1000000, CANTemp.FIdxChn,
                  CANTemp.FIdentifier,
                  CANTemp.FProperties,
                  CANTemp.FDLC,
                  CANTemp.FData[0],
                  CANTemp.FData[1],
                  CANTemp.FData[2],
                  CANTemp.FData[3],
                  CANTemp.FData[4],
                  CANTemp.FData[5],
                  CANTemp.FData[6],
                  CANTemp.FData[7],
                  CANTemp.FTimeUs)
    # 结束读取
    tslog_blf_read_end(blfID)

# _curr_path = os.path.dirname(__file__)
writeFileName = ("C:/Users/tosun/Desktop/[2014 s t]/1234567.blf").encode("utf8")
writeHandle = c_ulong(0)

# 写入数据到blf文件
def write_blf_datas():
    r = tslog_blf_write_start(writeFileName, writeHandle)
    if r == 0:
        global blfID, count
        realCount = c_long(0)                      # 读取的报文指针
        messageType = c_long(_TSupportedObjType.sotUnknown.value)    # 当前报文类型
        CANTemp = TLIBCAN()                         # CAN报文数据
        CANFDTemp = TLIBCANFD()                     # CANFD报文数据
        LINTemp = TLIBLIN()                         # LIN报文数据

        for i in range(count.value):
            # 读当前报文的类型，并赋值给报文指针
            tslog_blf_read_object(blfID, realCount, messageType, CANTemp, LINTemp, CANFDTemp)   # 读当前报文的类型，并赋值给报文指针
            if messageType.value == (c_long(_TSupportedObjType.sotCAN.value)).value:
                CANTemp.FIdxChn = 2
                tslog_blf_write_can(writeHandle, CANTemp)
        # 结束读取
        tslog_blf_read_end(blfID)
        # 结束写入
        tslog_blf_write_end(writeHandle)
        logger.info("blf_write_successful")
    else:
        logger.info(r)



if __name__ == "__main__":
    initialize_lib_tsmaster(AppName)

    # 枚举当前插在电脑上的能够使用的 CAN 设备数量
    ACount = c_int32(0)
    tsapp_enumerate_hw_devices(ACount)
    print("在线硬件设备数量有" , ACount)

    PTLIBHWInfo = TLIBHWInfo()
    for i in range(ACount.value):
        tsapp_get_hw_info_by_index(i, PTLIBHWInfo)
        print(PTLIBHWInfo.FDeviceType,
              PTLIBHWInfo.FDeviceIndex,
              PTLIBHWInfo.FVendorName.decode("utf8"),
              PTLIBHWInfo.FDeviceName.decode("utf8"),
              PTLIBHWInfo.FSerialString.decode("utf8"))


    logger.info("0: 连接硬件")
    logger.info("1: 发送报文")
    logger.info("2: 停止周期发送")
    logger.info("3: 接收CAN/CANFD报文")
    logger.info("4: 载入dbc文件")
    logger.info("5: 卸载dbc文件")
    logger.info("6: 开始录制报文")
    logger.info("7: 停止录制报文")
    logger.info("8: 新建诊断模块")
    logger.info("9: 请求响应数据")
    logger.info("q: 退出程序")
    logger.info("a: 读取blf")
    logger.info("b: 获取blf中的数据")
    logger.info("c: 写blf，在此环境下需先读取blf")
    logger.info("注意后续对硬件操作必须先连接硬件，但如果需要加载/卸载dbc文件需先加载/卸载dbc再开启硬件\n")

    while True:
        key = input("请输入要执行的操作序号")
        if key == '0':
            connect()
        elif key == '1':
            send_canfd_Message()
        elif key == '2':
            stop_cyclic_msg_CANFD()
        elif key == '3':
            receive_canfd_message()
            receive_can_message()
        elif key == '4':
            load_dbc()       # 函数有问题——结合系统变量去查错误原因
        elif key == '5':
            unload_dbc()
        elif key == '6':
            start_logging()
        elif key == '7':
            stop_loggging()
        elif key == '8':
            create_uds_module()
        elif key == '9':
            req_and_res_can()
        elif key == 'a':
            read_blf()
        elif key == 'b':
            read_blf_datas()
        elif key == 'c':
            write_blf_datas()
        elif key == 'q':
            logger.info(count1)
            break
    tsapp_disconnect()
    finalize_lib_tsmaster()

