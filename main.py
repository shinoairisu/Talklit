import streamlit as st
import pandas as pd
import numpy as np
from tinydb import TinyDB, Query
import hashlib
import time
import _thread
from datetime import datetime
#会话存储原理：按 年-月-日键值对 存储在数据库中。每次打开只能看见当天的聊天信息。

def get_date():
     strs=f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}"
     return strs

#查询数据
def get_data():
     db = TinyDB('userdb.json')
     Talk = Query()
     date_str=get_date()
     sout=db.search(Talk.date==date_str)
     if len(sout)==0:
          db.insert({'date':date_str,'data':[f"系统\t@all今天是{date_str}，欢迎大家光临！"]})
          sout=db.search(Talk.date==date_str)
          db.close()
          return sout
     else:
          db.close()
          return sout

#插入数据
def insert_data(strs):
     db = TinyDB('userdb.json')
     Talk = Query()
     date_str=get_date()
     sout=db.search(Talk.date==date_str)
     if len(sout)==0:
          db.insert({'date':date_str,'data':[f"系统\t@all今天是{date_str}，欢迎大家光临！"]})
          db.update({'data':[strs]},Talk.date==date_str)
          db.close()
     else:
          sout[0]['data'].append(strs)
          db.update({'data':sout[0]['data']},Talk.date==date_str)
          db.close()


#获取聊天内容
def get_markdown():
     sout=get_data()
     talks=""
     for i in sout:
          for j in i["data"][::-1]:
               cont=j.split("\t")
               if cont[1].find("@all")>=0 or cont[1].find(f"@{st.session_state['sid']}")>=0 or cont[0]==f"{st.session_state['sid']}":
                    talks+=f"### {cont[0]}说：\n"
                    newcont=cont[1].replace("@all","")
                    newcont=newcont.replace(f"@{st.session_state['sid']}","")
                    talks+=f"{newcont}\n"

     return talks


def index():
     st.title('欢迎使用Talklit聊天室！')
     islog=""
     if 'sid' not in st.session_state:
          islog="您还未登录，请注册或登录:"
     else:
          islog=f"亲爱的{st.session_state['sid']}，欢迎进入聊天室！请开始随意聊天吧！"
     sbx = st.selectbox(
    islog,
    ("主页","注册", "登录", "聊天室"))

     con = st.empty()
     if sbx=="主页":
          con.empty()
          ccon=con.container()
          ccon.title("在这里，可以发现新的朋友！")
          strs="## 现有注册用户id有:\n"
          db = TinyDB('userdb.json')
          em = db.all()
          for i in em:
               if 'sid' in i:
                    strs+=f"* {i['sid']}\n"
          db.close()
          strs+="## 使用说明：\n默认所有信息为广播。\n\n可以使用@+id单独讲消息推送给某人。\n\n由于条件限制，除了首次登录，需要手动刷新聊天界面数据。"
          ccon.markdown(strs)
     elif sbx=="注册":
          signup(con)
     elif sbx=="登录":
          login(con)
     elif sbx=="聊天室":
          chatroom(con)


#注册
def signup(con):
     con.empty()
     ccon=con.container()
     if 'sid' not in st.session_state:
          ccon.title('请注册！')
          form = ccon.form("sign_form")
          sid=form.text_input("账号")
          passw=form.text_input("密码",type="password")
          passw2=form.text_input("再次输入密码",type="password")
          submitted = form.form_submit_button("提交")
          if submitted:
               if sid!='' and passw!='' and passw2!='':
                    db = TinyDB('userdb.json')
                    User = Query()
                    sout=db.search(User.sid==sid)
                    if len(sout)!=0:
                         form.error('用户id已经存在请重新输入！')
                    else:
                         if passw==passw2:
                              pws=hashlib.sha1(passw.encode("utf-8")).hexdigest()
                              db.insert({'sid': sid.strip(), 'pws': pws})
                              form.success('注册成功，请登录！')
                              
                         else:
                              form.error('两次密码不一致，请重新输入')
                    db.close()
               else:
                    form.error('信息未填写完全，请重新填写。')
     else:
          ccon.success('您已登录。请刷新登出后再注册新账号。')
          


#登录
def login(con):
     con = st.empty()
     ccon=con.container()
     if 'sid' not in st.session_state:
          ccon.title('请登录！')
          form = ccon.form("login_form")
          sid=form.text_input("账号")
          passw=form.text_input("密码",type="password")
          submitted = form.form_submit_button("提交")
          if submitted:
               if sid!="" and passw!="":
                    db = TinyDB('userdb.json')
                    User = Query()
                    sout=db.search(User.sid==sid.strip())
                    if len(sout)!=0 and sout[0]['pws']==hashlib.sha1(passw.encode("utf-8")).hexdigest():
                         st.session_state['sid']=sid
                         form.success('成功登录，请进入聊天室聊天吧！')
                    else:
                         form.error('用户名或密码错误！')

                    db.close()
               else:
                    form.error('信息未填写完全，请重新填写。')
     else:
          ccon.success('您已经登录，请勿重复登录。')

def chatroom(con):
     con.empty()
     ccon=con.container()
     if 'sid' not in st.session_state:
          ccon.title('您未登录，请先注册。')
     else:
          form=ccon.form("chat")
          contents=form.text_input("输入你想说的话吧，对某人说请加上@xx")
          #存储结构：  发送者\t发送内容。@all就是群发，@id就是某人单独的。不加@就是默认all。
          submitted = form.form_submit_button("发射")
          flash=ccon.button('刷新聊天内容')
          mark=get_markdown()
          if mark=="":
               ccon.write("此地还是荒原，赶紧聊天填充吧！")
          mk=ccon.markdown(mark)
          if submitted:
               strs=""
               if contents!="":
                    if contents.find("@")>=0:
                         strs=st.session_state['sid']+"\t"+contents
                         insert_data(strs)
                    else:
                         strs=st.session_state['sid']+"\t@all"+contents
                         insert_data(strs)
                    form.success('发射成功')
               else:
                    form.error('不能发送空字符串！')
               mk.empty()
               mk=ccon.markdown(get_markdown())
          if flash:
               form.success('刷新完成！')
               mk.empty()
               mk=ccon.markdown(get_markdown())




if __name__=="__main__":
     st.set_page_config(
     page_title="Talkerlit",
     page_icon="🧊",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': 'https://www.baidu.com/',
     }
 )
     index()