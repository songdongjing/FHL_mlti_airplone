from __future__ import print_function
from concurrent import futures
import ipaddress
import logging
from multiprocessing.connection import wait
from urllib import response
from xmlrpc.client import ResponseError
import grpc
import time
import socket
import json
import threading
import sys
import os
import jsonservice_pb2, jsonservice_pb2_grpc
import competition
#coding=utf-8

import queue;

PP_USER_NETWORK_LOGIN = 102;				

PP_USER_NETWORK_LOGOUT = 103;	

PP_USER_NETWORK_LOGIN_REQUEST = 111;		

PP_USER_NETWORK_LOGIN_RESPONSE = 112;

PT_INIT_SCENE = 106;			

PT_INIT_SCENE_RESPONSE = 107;

PT_PLATFORM_STATE_INFO = 120;	

PT_COLLABORATIVE_SHARE = 130;	

PT_COLLABORATIVE_SHARE_RESULT =131;

PT_TASK_STATE = 129;

PT_PLATFORM_CONTROL = 121;		

PT_CONSENSUS_INFO = 140;		

PT_CONSENSUS_RESULT = 141;	

PT_INIT_SCENE_SCHEDULE = 160;	

mamnager_module = 0;                #指控中心


class JSONSERVER_PYTHON(jsonservice_pb2_grpc.JSONSERVICEServicer):
    
    def __init__(self):       
        self.__m_recv_messages = queue.Queue();
        self.m_lock = threading.Lock(); 
        super().__init__();      
    
    def init_owner(self,owner):
        self.owner = owner;

    def get_json(self, request, context):
        if(len(request.json_message)>2):
            #print(request.json_message);
            msg = json.loads(request.json_message); 
            self.owner.recv(msg);
        return jsonservice_pb2.JSONRESPONSE(json_message = "ok");

    def get_json_stream(self, request_iterator, context):
        if(len(request.json_message)>2):
            for request in request_iterator:
                msg = json.loads(request.json_message); 
                self.owner.recv(msg);
        
        return jsonservice_pb2.JSONRESPONSE(json_message = "ok");

    def recv(self,msg):
        self.m_lock.acquire();
        self.__m_recv_messages.put(msg);      
        self.m_lock.release();

    def __recv_get(self):
        if(not self.__m_recv_messages.empty()):
            return self.__m_recv_messages.get(); 
        return None;

def make_network_message(message):
    return jsonservice_pb2.JSONREQUEST(json_message = message.encode('utf-8').decode('unicode-escape'));

def generate_loginmessages(scene_name,ip_addr):
    #lname = socket.gethostname();
    #ipd = socket.gethostbyname(lname);
    loginmsg = {"protocol_type":PP_USER_NETWORK_LOGIN,"identity":0,'seatid':0,'ip':ip_addr,'port':0,"task_name": scene_name, "team_name": "scene_name"};
    loginmsg['username'] = "login";
    loginmsg['sender'] = "login";
    loginmsg['receiver'] = "login";
    loginmsg['sender_id'] = 0;
    loginmsg['receiver_id'] = 0;
    json_str = json.dumps(loginmsg);
    return make_network_message(json_str);

def generate_loginAImessages(ip_addr,port,scene_name):
    loginmsg = {"protocol_type":PP_USER_NETWORK_LOGIN_REQUEST,'ip':ip_addr,'port':port,"task_name": scene_name, "team_name": "test"};
    loginmsg['ip'] = ip_addr;
    loginmsg['port'] = port;
    loginmsg['ip'] = ip_addr;
    loginmsg['port'] = port;
    json_str = json.dumps(loginmsg);
    return make_network_message(json_str);

def generate_initscene_messages(init_num,scene_name):
    msg = { "platforminit_num": init_num,"protocol_type": PT_INIT_SCENE_RESPONSE,"task_name": scene_name, "team_name": "test"};    
    json_str = json.dumps(msg);
    return make_network_message(json_str);

InitArea = []

def restart_program():
    time.sleep(2);
    pythonx = sys.executable;
    os.execl(pythonx,pythonx,*sys.argv);

class AIManagerModule(threading.Thread):   #threading.Thread
     
    def __init__(self):

        fullpath = "";
        if getattr(sys,'frozen',False):
            fullpath = os.path.dirname(sys.executable);
        elif __file__:
            fullpath = os.path.dirname(__file__);
        fullpath+="\config\config.json";

        with open("config\config.json",encoding='utf-8') as jsonfile:
            ipjson = json.load(jsonfile);
            self.ipadd = ipjson["ip"];
            ser_add = ipjson["server_address"];
            print("服务器地址地址",ser_add);
        self.m_channel = grpc.insecure_channel(ser_add);#创建一个gRPC通道（明文传输）
        self.m_manager_stub = jsonservice_pb2_grpc.JSONSERVICEStub(self.m_channel); #创建一个gRPC客户端存根，用于与gRPC服务器进行通信，gRPC通道为self.m_channel
        self.__m_send_messages = queue.Queue();
        self.__m_recv_messages = queue.Queue();

        self.m_load_mod = competition.equipment_schedule_interface();
        self.m_consensus_mod = competition.consensus_interface();    
        self.m_task_name = "test";
        self.m_first_connect = True;
        self.m_is_connect = False;
        self.m_is_runing = True;
        self.m_stream = 0;
        self.thread_send = threading.Thread(target=self.udp_send_hundle);
        self.__m_login_messages = queue.Queue();

        self.m_id = 0;
        self.m_motion_mod = competition.motion_interface();

        self.m_recv_lock = threading.Lock(); 
        self.m_send_lock = threading.Lock(); 

        super().__init__();       
        print("AIManagerModule create");

    def udp_send_hundle(self):
        while self.m_is_runing: 
            if(not self.__m_send_messages.empty()):            
                msg = self.__m_send_messages.get();#在队列中接受到需要发送的jsonrequest对象
                self.send_to_server(msg);
            if(not self.__m_recv_messages.empty()):            
                msg = self.__m_recv_messages.get();
                self.recv_from_server(msg);
            time.sleep(0.02);

    def __del__(self):
        pass
        # InitArea.clear();
        # wait();
        # # super().__del__()
        # print("AIManagerModule destroy");
    def send_to_server(self,msg):
        try:
            # print("发送数据给服务器")
            self.m_manager_stub.get_json(msg);
            # print("发送成功")
        except grpc.RpcError as error:
            print("发送给服务器时发生错误")
            print(error)
            restart_program()


    def recv_from_server(self,msg):
        if(msg["protocol_type"] == PT_INIT_SCENE ):
            self.init_scene(msg); 
            msg["platform_num"] = msg["sender_id"];
        elif(msg["protocol_type"] == PP_USER_NETWORK_LOGIN ):             
            self.jsonserver = JSONSERVER_PYTHON();
            self.jsonserver.init_owner(self);
            self.gserver = grpc.server(futures.ThreadPoolExecutor(max_workers=10));#开启服务器
            jsonservice_pb2_grpc.add_JSONSERVICEServicer_to_server(self.jsonserver,self.gserver);#绑定处理器self.jsonserver
            ipaddport = "[::]:{}".format(msg["port"]);
            # ipaddport = "127.0.0.1:{}".format(msg["port"]);
            print(ipaddport);
            self.gserver.add_insecure_port(ipaddport);
            self.gserver.start();
            self.gserver.wait_for_termination();
        elif(msg["protocol_type"] == PT_CONSENSUS_INFO ): 
            self.consensus(msg)
        elif( msg["protocol_type"] == PT_INIT_SCENE_SCHEDULE):
            self.m_id = msg["platform_num"];
            self.m_motion_mod.init(msg)    
        elif(msg["protocol_type"] == PT_PLATFORM_STATE_INFO ):  #通信消息传输！
            ret = self.m_motion_mod.share(msg); 
            ret["sender_id"] = self.m_id;
            ret["receiver_id"] = self.m_id;

            tempstr = ret["custom_content"];                            #先将custom_content字段值取出
            ret["custom_content"] = "tihuanzhuanyongziduan";            #再进行字符替换
            motionstr = json.dumps(ret,indent=4);                       #整体json都dumps成功之后
            motionstr = motionstr.replace("tihuanzhuanyongziduan",tempstr); #将原本的字段替换进来 即可

            motion = make_network_message(motionstr);#将json消息转化为jsonrequest消息对象
            self.send(motion);
        elif(msg["protocol_type"] == PT_COLLABORATIVE_SHARE_RESULT ):    
            ret = self.m_motion_mod.motion(msg);
            ret["sender_id"] = self.m_id;
            ret["receiver_id"] = self.m_id; 
            motionstr = json.dumps(ret,indent=4);
            motion = make_network_message(motionstr);
            self.send(motion); 
        elif(msg["protocol_type"] == PT_TASK_STATE ): 
            if(msg["task_state"] == 200): #结束
                self.m_is_runing = False;
                time.sleep(1);
                self.gserver.stop(0);
                time.sleep(0.2);
                sys.exit();

    def generate_messages(self):    	
        while(self.m_is_runing): 
            time.sleep(0.002);
            if(not self.__m_login_messages.empty()):
                yield self.__m_login_messages.get();
        print("end rpc stream")

    def grpc_server_on(self)->bool:
        try:
            grpc.channel_ready_future(self.m_channel).result(timeout=3);
            return True;
        except grpc.FutureTimeoutError:
            return False;

    def run(self):
        print("run AIManagerModule"); 
        login = generate_loginmessages(self.m_task_name,self.ipadd); 
        self.__m_login_messages.put(login)
        print("login:",login);
        
        ready = self.grpc_server_on();

        while(not ready):
            ready = self.grpc_server_on();
            print("ready:",ready);

        self.thread_send.start();

        #responses = self.m_manager_stub.get_json_stream(self.generate_messages());  #self.generate_messages()
        try:      
            response = self.m_manager_stub.get_json(login);
            if(response):
                msg = json.loads(response.json_message);  
                print("登录后返回的消息",msg);
                self.recv_from_server(msg);
            #for response in responses:
            #    msg = json.loads(response.json_message);  
            #    self.recv_from_server(msg);                
        
            
        except grpc.RpcError as error:
            print(error)
            restart_program()
        
    def consensus(self,scene_info):
        msg = self.m_consensus_mod.consensus(scene_info,self.m_task_name);
        msg["sender_id"] =  scene_info["sender_id"];
        msg["receiver_id"]  = scene_info["receiver_id"];
        con_re = json.dumps(msg);

        con_resp = make_network_message(con_re);
        self.send(con_resp);    


    def init_scene(self,scene_info):
        
        InitArea.clear();
        num = 0;
        #读取任务区域点集
        for pos in scene_info["task_area"]:
            InitArea.append(pos);
            num = pos["index"];
            InitArea[num]["platform_lon"] = pos["task_area_point_lon"];
            InitArea[num]["platform_lat"] = pos["task_area_point_lat"];
            InitArea[num]["platform_alt"] = pos["task_area_point_alt"];
            #num = len(InitArea);      
        self.m_task_name = scene_info["task_name"]; 
   
        num = len(scene_info["ai_modules"]);
        print(num)

        #读取计算传感器搭载配置方案    
        init_resp = self.m_load_mod.eq_schedule(scene_info,num,self.m_task_name);
                
        init_resp["sender_id"] = scene_info["sender_id"];
        init_resp["receiver_id"] = scene_info["receiver_id"];
        init_re = json.dumps(init_resp);
        init_resp = make_network_message(init_re);
        self.send(init_resp);

    def send(self,msg):
        self.m_send_lock.acquire();
        self.__m_send_messages.put(msg);   #将消息对象放入发送队列
        self.m_send_lock.release();

    def recv(self,msg):        
        self.m_recv_lock.acquire();        
        self.__m_recv_messages.put(msg);  #将消息对象放入接受对象
        self.m_recv_lock.release();

    def __recv_get(self):
        if(not self.__m_recv_messages.empty()):
            return self.__m_recv_messages.get(); 
        return None;    
    
mamnager_module = AIManagerModule();
mamnager_module.start(); #开启控制中心线程

def main():       
    logging.basicConfig(level=logging.INFO)
    # for m in range(46):
    #     mamnager_module = AIManagerModule();
    #     mamnager_module.start(); #开启控制中心线程


if __name__ == '__main__':
    main()
    
