# -*- coding: utf-8 -*-
import re
import requests
import json #用于读取账号信息
import time #用于计时重新发送requests请求
import datetime
import base64 #用于解密编码
import smtplib
import ssl
from email.mime.text import MIMEText
from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError


ifmts = [
    ['201847020113','02051054',       '15039672156',['','成功'],'g','41','4117','河南省驻马店平舆县'],
    ['201847020114','03208049',       '13298332585',['','成功'],'g','41','4108','河南省焦作市解放区'],
    ['201847020115','1203001X',       '18336667654',['','成功'],'g','41','4113','河南省南阳市新野县'],
    ['201847020118','Nolover200094!', '18629020415',['','成功'],'g','12','1201','天津市河北区北宁湾'],
    ['201884130331','1207002X',       '17550327997',['','成功'],'g','41','4101','河南郑州市郑州大学'],
    ['201984160411','12160033',       '15038715516',['','成功'],'g','41','4113','河南省南阳市新野县'],
    ['201984130524','02013129',       '17516208112',['','成功'],'g','41','4113','河南省南阳市新野县'],
    ['201802020129','87324@qweASDzxc','18739035312',['','成功'],'g','41','4113','河南省南阳市新野县'],
]

baogao = '新年快乐\n'
Baogao = '新年快乐\n\n'

#短信
appid = '1400601132'  # 自己应用ID
appkey = '13e2a897ede0197782fe093a934a5859'  # 自己应用Key
sms_sign = '打卡报告'  # 自己腾讯云创建签名时填写的签名内容
sender = SmsSingleSender(appid, appkey)
template_id = '1217189'  #模板ID

def mb_msg(phone_num,template_param_list):
    response = sender.send_with_param(86, phone_num, template_id, template_param_list, sign=sms_sign)



'''
curr_dir = os.path.dirname(os.path.abspath(__file__))
r=""
'''


for ifmt in ifmts:
    id = ifmt[0]
    pwd = ifmt[1]
    phone_num = ifmt[2]
    template_param_list = ifmt[3]
    template_param_list[0] = ifmt[0]
    
    #login

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',	
        'referer':'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=a',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    form={
        "uid": id,
        "upw": pwd,
        "smbtn": "进入健康状况上报平台",
        "hh28": "750"  #按照当前浏览器窗口大小计算
    }
    r = ""
    max_punch = 10
    curr_punch = 0 #if curr_punch > max_pubch then exit

    while True:
        try:
            r= requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login",headers=headers,data=form,timeout=(200,200)) #response为账号密码对应的ptopid和sid信息,timeout=60(sec)
            
        except:
            curr_punch+=1
            if curr_punch>max_punch:
                exit()
            time.sleep(120)     #sleep 60 sec
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding) #解决乱码问题
    r.close()
    del(r)
    #first6
    matchObj = re.search(r'ptopid=(\w+)\&sid=(\w+)\"',text)
    try:
        ptopid = matchObj.group(1) 
        sid = matchObj.group(2) 
    except:
        time.sleep(1)
        exit()

    headers= {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',	
        'referer':'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch=0
    while True:
        try:
            r = requests.get("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid="+ptopid+"&sid="+sid+"&fun2=") #response里含有jksb对应的params
        except:
            if curr_punch>max_punch:
                exit()
            curr_punch+=1
            time.sleep(120)
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding) #解决乱码问题
    r.close()
    del(r)
    #jksb?with_params 
    matchObj = re.search(r'ptopid=(\w+)\&sid=(\w+)\&',text)
    ptopid = matchObj.group(1) 
    sid = matchObj.group(2) 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',	
        'referer':'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch=0
    while True:
        try:
            r = requests.get("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid="+ptopid+"&sid="+sid+"&fun2=",headers=headers) #response为jksb表单第一页
        except:
            while curr_punch>max_punch:
                exit()
            curr_punch+=1
            time.sleep(120)
        else:
            break
    ptopid1 = ptopid
    sid1 = sid

    text = r.text.encode(r.encoding).decode(r.apparent_encoding) #解决乱码问题
    r.close()
    del(r)
    #DONE
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\".+',text)
    ptopid = matchObj.group(1) 
    sid = matchObj.group(2) 
    form = {
        "day6": "b",
        "did": "1",
        "door": "",
        "men6": "a",
        "ptopid": ptopid,
        "sid": sid
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid='+ptopid1+'&sid='+sid1+'&fun2=',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    while True:
        try:
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb",headers=headers,data=form) #response为打卡的第二个表单
        except:
            while curr_punch>max_punch:
                exit()
            curr_punch+=1
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding) #解决乱码问题
    r.close()
    del(r)
    #DONE
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\"',text)
    ptopid = matchObj.group(1) 
    sid = matchObj.group(2) 
    form = {
        "myvs_1": "否",
        "myvs_2": "否",
        "myvs_3": "否",
        "myvs_4": "否",
        "myvs_5": "否",
        "myvs_6": "否",
        "myvs_7": "否",
        "myvs_8": "否",
        "myvs_9": "否",
        "myvs_10": "否",
        "myvs_11": "否",
        "myvs_12": "否",
        "myvs_13": ifmt[4],
        "myvs_13a": ifmt[5],
        "myvs_13b": ifmt[6],
        "myvs_13c": ifmt[7],
        "myvs_24": "否",
        "myvs_26": "5",
        "memo22": "[待定]",
        "did": "2",
        "door": "",
        "day6": "b",
        "men6": "a",
        "sheng6": "",
        "shi6": "",
        "fun3": "",
        "jingdu": "0.0000",
        "weidu": "0.0000",
        "ptopid": ptopid,
        "sid": sid
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Referer':'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    while True:
        try:
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb",data=form,headers=headers) #response为完成打卡页面
        except:
            while curr_punch>max_punch:
                exit()
            curr_punch+=1
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding) #解决乱码问题
    r.close()
    del(r)
    id = '•'*8 + id[8:]
    if("感谢你今日上报健康状况！" in text):
        baogao = baogao+id+':打卡成功'+'\n'
        Baogao = Baogao+id+':打卡成功'+'\n\n'
        mb_msg(phone_num, template_param_list)
        #print(id+":打卡成功")
    else:
        baogao = baogao+id+':打卡失败'+'\n'
        Baogao = Baogao+id+':打卡失败'+'\n\n'
        template_param_list[1] = '失败'
        mb_msg(phone_num, template_param_list)	    
        #print(id+":打卡失败")



tiMe = str(datetime.datetime.strptime(time.strftime('%Y/%m/%d %H:%M:%S',time.localtime()),'%Y/%m/%d %H:%M:%S')+datetime.timedelta(hours=8))
baogao += tiMe
Baogao += tiMe

#QMSG
data={
    "msg":baogao, #需要发送的消息
    "qq":"952172515"#需要接收消息的QQ号码
}
KEY='c49a56e18a5ecb95158e6b534692b00b'
url2='https://qmsg.zendee.cn/group/'+KEY
response = requests.post(url2,data=data)

#微信server酱
requests.post('http://sc.ftqq.com/SCT87757TzQZqm0wLV0yA1TiTWx0gongj.send', data={'text': "打卡", 'desp': Baogao})
requests.post('http://sc.ftqq.com/SCT97173TrbSWrZotAN9yfFwQzb6IuF19.send', data={'text': "打卡", 'desp': Baogao+'\n\n*新年快乐*'})

#邮件
mail_host = 'smtp.qq.com'  
mail_user = 'wavevariation'  
mail_pass = 'jxroiqmqrgydbcch'   
sender = 'wavevariation@qq.com'  
receivers = ['yingwun@foxmail.com', \
             '2051341541@qq.com', \
             '1994423126@qq.com', \
             '703269880@qq.com', \
             '3082453633@qq.com', \
             '2878446814@qq.com', \
             '760955752@qq.com', \
             '1538785649@qq.com']  

message = MIMEText(baogao+'\n(ง •_•)ง','plain','utf-8')      
message['Subject'] = '每日打卡情况报告' 
message['From'] = sender      
message['To'] = receivers[0]  

try:
    smtpObj = smtplib.SMTP() 
    smtpObj = smtplib.SMTP_SSL(mail_host)
    smtpObj.login(mail_user,mail_pass) 
    smtpObj.sendmail(
        sender,receivers,message.as_string()) 
    smtpObj.quit() 
  
except smtplib.SMTPException as e:
    a = e