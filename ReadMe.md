## 说明
套壳TOSUN的python接口，支持CMD的参数控制


### Requests
1. 用server接命令行参数，client发参数
2. 处理接受的参数，识别并返回响应的处理code
3. 给第2条的code以及发参单独建一个py文件，做好说明，并且help可查询
4. 功能包括：
   ~~1. connect~~
   ~~2. 发送单帧CAN~~
   ~~3. 循环发送CAN~~
   ~~4. 停发~~
   ~~5. disconnect~~
   ~~6. 关闭server端~~
   7. 打开同星工程
   8. 关闭同星工程
   9. 给系统变量一个值，出发CAPL脚本里的指令


### ToDo
1. 完善log
2. 增加停发和关闭整个sever的功能
3. 完善demo文件，新建类CAN, CAMessage, CANFD, CANFDMessage等
4. 做一个父类，尝试vector产品和TOSUN产品作为子类



