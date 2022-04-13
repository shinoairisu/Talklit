import streamlit as st
import pandas as pd
import numpy as np
from tinydb import TinyDB, Query
import hashlib

def index():
     st.set_page_config(
     page_title="Talkerlit",
     page_icon="🧊",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': 'https://www.baidu.com/',
     }
 )
     st.title('欢迎使用Talklit聊天室！')
     sbx = st.selectbox(
    "请注册或登录:",
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
               strs+=f"* {i['sid']}\n"
          strs+="## 使用说明：\n默认所有信息为广播。\n可以使用@+id单独讲消息推送给某人。"
          ccon.markdown(strs)
     elif sbx=="注册":
          signup(con)
     elif sbx=="登录":
          login(con)
     elif sbx=="聊天室":
          pass


#注册
def signup(con):
     con.empty()
     ccon=con.container()
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
                    # hashlib.sha1('12345'.encode("utf-8")).hexdigest()
               # if sid!="" and passw==passw2:
               #      form.success('注册成功，请刷新后登录！')
               # else:
               #      form.error('未知错误，注册失败！')
          else:
               form.error('表格未填写完全，请重新填写。')
          


#登录
def login(con):
     con = st.empty()
     ccon=con.container()
     ccon.title('请登录！')

def chatroom(com):
     pass



if __name__=="__main__":
     index()