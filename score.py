#! /usr/bin/env python3
# -*- coding: utf8 -*-
from tkinter import *
from PIL import Image, ImageTk
import requests as rq
from bs4 import BeautifulSoup

COOKIES = {}
class makeLoginPanel:

    def __init__(self,master):
        global COOKIES
        self.master = master
        with  open('image.jpg','wb') as f:
            r = rq.get('http://jwxt.bupt.edu.cn/validateCodeAction.do')
            COOKIES = rq.utils.dict_from_cookiejar(r.cookies)
            print(COOKIES)
            f.write(r.content)
        frame = Frame(master)
        frame.pack()
        
        # variable to store checkbox value
        # self.keeplogin = IntVar()

        self.UserLabel = Label(frame,
            text="Username")
        self.PassLabel = Label(frame,
            text="Password")
        self.HashLabel = Label(frame,
            text="HashCode")
        self.UserLabel.grid(row=0,column=0,sticky=W)
        self.PassLabel.grid(row=1,column=0,sticky=W)
        self.HashLabel.grid(row=2,column=0,sticky=W)

        self.UserEntry = Entry(frame)
        self.PassEntry = Entry(frame,show='*')
        self.HashEntry = Entry(frame)
        self.UserEntry.grid(row=0,column=1,columnspan=2)
        self.PassEntry.grid(row=1,column=1,columnspan=2)
        self.HashEntry.grid(row=2,column=1,columnspan=2)

        self.ImgBox = ImageTk.PhotoImage(file='image.jpg')
        self.ImgLabel = Label(frame, image=self.ImgBox)
        self.ImgLabel.image = self.ImgBox
        self.ImgLabel.grid(row=3,column=0,columnspan=2)
        
        self.RefreshBtn = Button(frame, text="Refresh",command=self.refresh)
        self.RefreshBtn.grid(row=3,column=2,sticky=W+E)

        # self.KeepLoginChkBtn = Checkbutton(frame,text='KeepLogin',variable=self.keeplogin)
        # self.KeepLoginChkBtn.grid(row=4,column=0)

        self.LoginBtn = Button(frame,text='Login',command=self.login)
        self.LoginBtn.grid(row=4,column=1,columnspan=2,sticky=W+E)

    def refresh(self):
        with  open('image.jpg','wb') as f:
            r = rq.get('http://jwxt.bupt.edu.cn/validateCodeAction.do',cookies=COOKIES)
            # f.write(io.StringIO(r.content))
            f.write(r.content)
        self.ImgBox = ImageTk.PhotoImage(file='image.jpg')
        self.ImgLabel.config(image=self.ImgBox)
    def login(self):
        global COOKIES
        username = self.UserEntry.get()
        password = self.PassEntry.get()
        hashcode = self.HashEntry.get()

        # just for test locally
        # payload = {
        # "type": "sso",
        # "zjh": username,
        # "mm": password,
        # "v_yzm": hashcode
        # }
        with open('test/account.txt','r') as f:
            data = f.read().split(':')
            print(data)
        payload = {
        "type": "sso",
        "zjh": data[0],
        "mm": data[1],
        "v_yzm": hashcode
        }

        r = rq.post('http://jwxt.bupt.edu.cn/jwLoginAction.do',data=payload,allow_redirects=False,cookies=COOKIES)
        if not ('URP 综合教务系统 - 登录' in r.text):
            # print(r.text)
            print('login success')
            LoginRoot.destroy()
        else:

            print('login failed')

class makeMainPanel:
    def __init__(self,master):
        frame = Frame(master)
        frame.pack()

        # Test Command Here
        # print(self.getStuName())
        # print(self.getCourseInfo())

        # layout here
        self.SimpleBtn = Button(frame,text='Simple Mode',command=self.makeSimplePanel)
        self.SimpleBtn.grid(row=0,column=0)

        self.ProBtn = Button(frame,text='Pro Mode',command=self.makeProPanel)
        self.ProBtn.grid(row=0,column=1)


    def makeSimplePanel(self):
        self.SimpleRoot = Toplevel()
        makeSimplePanel(self.SimpleRoot)

    def makeProPanel(self):
        self.ProRoot = Toplevel()
        makeProPanel(self.ProRoot)

def getStuName():
    html = rq.get('http://jwxt.bupt.edu.cn/menu/s_top.jsp',cookies=COOKIES).text
    soup = BeautifulSoup(html)
    name = soup.select('a[onclick="logout()"]')[0].previous_sibling.strip()
    return name.split('\xa0')[1]

def getCourseInfo():

    # this function should return availiable course info
    # that is, courses that has been evaluated will be ignored

    html = rq.get('http://jwxt.bupt.edu.cn/jxpgXsAction.do?oper=listWj',cookies=COOKIES).text
    soup = BeautifulSoup(html)
    CourseInfo = []
    img = soup.select('img[title="评估"]')
    for i in img:
        content = i['name'].split('#@')
        CourseInfo.append({
            "num1": content[0],
            "num2": content[1],
            "num3": content[5],
            "TeacherName": content[2],
            "CourseName": content[4]
            })
    return CourseInfo
root = Tk()
LoginRoot = Toplevel()
LoginPanel = makeLoginPanel(LoginRoot)
def callback(event):
    print('callback function')
    MainPanel = makeMainPanel(root)
    root.deiconify()
    LoginRoot.unbind("<Destroy>",TopDestroy)
root.withdraw()
TopDestroy = LoginRoot.bind("<Destroy>",callback)
root.mainloop()
