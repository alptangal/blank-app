import asyncio
import os,sys,subprocess
import re,json
import random
from guild import *
import server
import aiohttp
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from typing import Callable

import threading
from dotenv import load_dotenv
import lark_basic
from pydantic import BaseModel
from contextlib import asynccontextmanager
load_dotenv()

print(111111)
APP_TOKEN=os.getenv('lark_base_token').strip().replace("'",'"')
APP_ID=os.getenv('lark_app_id').strip().replace("'",'"')
APP_SECRET=os.getenv('lark_app_secret').strip().replace("'",'"')
LARK=lark_basic.LarkClass(APP_ID,APP_SECRET)
processing_table_id=None
bot_table_id=None
lark_apps_table_id=None
PROCESSING_TIME_OUT=1800
STT=0

class CustomRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = asyncio.Lock()
        self.waiting_requests = 0 
        self.request_queue = []

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Kiểm tra nếu phương thức HTTP là POST
            if request.method == "POST":
                request_info = {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "body": await request.body(),  # Lưu body nếu cần thiết
                    "task": None  # Lưu task liên kết với request này
                }
                self.request_queue.append(request_info)
                self.waiting_requests += 1
                print(f"Hiện tại có {self.waiting_requests} POST request đang chờ xử lý.")
                print("Chi tiết request đang chờ xử lý:")
                for idx, req in enumerate(self.request_queue, 1):
                    print(f"{idx}. {req['method']} {req['url']}")
                async def handle_request_with_timeout():
                    try:
                        await asyncio.wait_for(self.lock.acquire(), timeout=30.0)
                    except asyncio.TimeoutError:
                        # Nếu timeout, xóa request khỏi danh sách và trả về lỗi
                        print(f"Timeout: Request {request_info['url']} bị loại bỏ khỏi hàng đợi.")
                        self.request_queue.remove(request_info)
                        self.waiting_requests -= 1
                        print(f"Hiện tại có {self.waiting_requests} POST request đang chờ xử lý.")
                        return Response(content="Request bị timeout do khóa không được giải phóng", status_code=408)
                    else:
                        response: Response = await original_route_handler(request)
                        self.lock.release()
                        self.request_queue.remove(request_info)
                        self.waiting_requests -= 1
                        print(f"Hiện tại có {self.waiting_requests} POST request đang chờ xử lý.")
                        return response
                request_info["task"] = asyncio.create_task(handle_request_with_timeout())
                return await request_info["task"]
            else:
                return await original_route_handler(request)
        return custom_route_handler
async def load_data():
    global processing_table_id,bot_table_id,lark_apps_table_id
    tables=await LARK.get_tables(APP_TOKEN)
    for table in tables:
        if table['name']=='processing':
            processing_table_id=table['table_id']
        elif table['name']=='bots':
            bot_table_id=table['table_id']
        elif table['name']=='lark_apps':
            lark_apps_table_id=table['table_id']
async def must_complete(func,**kwargs):
    while True:
        rs=await func(**kwargs)
        if rs and 'status' not in rs:
            return rs
        elif rs and 'status' in rs:
            await asyncio.sleep(rs['reconnect_after'])
        else:
            await asyncio.sleep(1)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_data()
    yield  
    print("Dọn dẹp dữ liệu khi ứng dụng dừng...")
app = FastAPI(lifespan=lifespan)
app.router.route_class = CustomRoute

class New_Process(BaseModel):
    id:str
    life_time:int
class Update_Process(BaseModel):
    record_id:str
    data:object
@app.get("/")
async  def greet_json():
    return {"Hello": "World!"}
@app.post('/create-process')
async  def greet_json1(data:New_Process):
    global STT,LARK
    processing_id=data.id
    life_time=data.life_time
    lark_apps=[]
    page_token=None
    conditions_array=[
        {
            'field_name':'OWNER',
            'operator':'isNotEmpty',
            'value':[]
        }
    ]
    while True:
        rs=await LARK.search_record(app_token=APP_TOKEN,table_id=lark_apps_table_id,conditions_array=conditions_array,page_token=page_token)
        if rs and 'items' in rs:
            lark_apps+=rs['items']
        if rs and rs['has_more']:
            page_token=rs['page_token']
        else:
            break
    conditions=[
        {
            "field_name": 'PROCESS_ID',
            "operator": "contains",
            "value":[processing_id]
        },
        {
            "field_name": 'STATUS',
            "operator": "doesNotContain",
            "value":['completed']
        },
    ]
    i=0
    error=None
    lark_app_for_response=lark_apps[STT]
    obj={
        'lark_app_id':lark_app_for_response['fields']['APP_ID'][0]['text'],
        'lark_app_secret':lark_app_for_response['fields']['APP_SECRET'][0]['text'],
        'lark_base_token':APP_TOKEN
    }
    STT=(STT+1) if STT<len(lark_apps)-1 else 0
    find_record=await must_complete(LARK.search_record,app_token=APP_TOKEN,table_id=processing_table_id,conditions_array=conditions)
    LARK=lark_basic.LarkClass(app_id=lark_app_for_response['fields']['APP_ID'][0]['text'],app_secret=lark_app_for_response['fields']['APP_SECRET'][0]['text'])
    if find_record and 'code' not in find_record:
        if find_record['total']==0:
            print({'PROCESS_ID':processing_id,'LIFE_TIME':life_time,'STATUS':'processing'})
            rs=await must_complete(LARK.create_new_record,app_token=APP_TOKEN,table_id=processing_table_id,value_fields={'PROCESS_ID':processing_id,'LIFE_TIME':life_time,'STATUS':'processing'})
            return {'status':'success','msg':'Create new process success','data':{'record_id':rs['record']['record_id'],'lark_app_info':obj}}
        else:
            tot=0
            for record in find_record['items']:
                now=int(datetime.now().timestamp())
                if now-record['fields']['UPDATED_AT']/1000>PROCESSING_TIME_OUT:
                    tot+=1
                    rs=await must_complete(LARK.update_record,app_token=APP_TOKEN,table_id=processing_table_id,record_id=record['record_id'],value_fields={'STATUS':'completed'})
                    if rs:
                        print(f'Process {processing_id} is expired then changed to "completed" status')
            if tot==len(find_record['items']):
                rs=await must_complete(LARK.create_new_record,app_token=APP_TOKEN,table_id=processing_table_id,value_fields={'PROCESS_ID':processing_id,'LIFE_TIME':life_time,'STATUS':'processing'})
                return {'status':'success','msg':'Create new process success','data':{'record_id':rs['record']['record_id'],'lark_app_info':obj}}
    return {'status':'error','msg':f'Something went wrong with this ID-{data.id}','raw_error':find_record}
@app.post('/update-process')
async  def update(data:Update_Process):
    record_id=data.record_id
    data_obj=data.data
    i=0
    rs=await must_complete(LARK.update_record,app_token=APP_TOKEN,table_id=processing_table_id,record_id=record_id,value_fields=data_obj)
    return {'status':'success','msg':f'Record- {record_id} updated'}
