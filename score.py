#! /usr/bin/env python
# -*- coding: utf8 -*-
from Tkinter import *
from PIL import Image, ImageTk
import requests as rq
from bs4 import BeautifulSoup
import io
from tkMessageBox import showwarning

COOKIES = {}
AVG_SCORE = -1
EXCLUDE1 = []
EXCLUDE2 = []
LOGIN = False

class makeLoginPanel:

    def __init__(self,master):
        global COOKIES
        self.master = master
        r = rq.get('http://jwxt.bupt.edu.cn/validateCodeAction.do')
        COOKIES = rq.utils.dict_from_cookiejar(r.cookies)
        print COOKIES 
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

        self.ImgBox = ImageTk.PhotoImage(data=r.content)
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
        r = rq.get('http://jwxt.bupt.edu.cn/validateCodeAction.do',cookies=COOKIES)
        self.ImgBox = ImageTk.PhotoImage(data=r.content)
        self.ImgLabel.config(image=self.ImgBox)
    def login(self):
        global COOKIES
        global AVG_SCORE
        global LOGIN
        username = self.UserEntry.get()
        password = self.PassEntry.get()
        hashcode = self.HashEntry.get()

        payload = {
        "type": "sso",
        "zjh": username,
        "mm": password,
        "v_yzm": hashcode
        }

        r = rq.post('http://jwxt.bupt.edu.cn/jwLoginAction.do',data=payload,allow_redirects=False,cookies=COOKIES)
        if not (u'URP 综合教务系统 - 登录' in r.text):
            print 'login success' 
            LOGIN = True
            AVG_SCORE = cal_avg_score(COOKIES)
            LoginRoot.destroy()
        else:
            showwarning(u"登录失败", u"用户名或密码或验证码错误")

            print 'login failed' 

class makeMainPanel:
    def __init__(self,master):
        frame = Frame(master=master, width=100, height=100)
        frame.pack()

        # Test Command Here
        # print(self.getStuName())
        # print(self.getCourseInfo())

        # layout here
        self.label = Label(frame, text=u"加权平均成绩：" + str(AVG_SCORE))
        self.label.pack()

        self.lblex1 = Label(frame, text=u"成绩不是数字的学科：" + u"，".join(EXCLUDE1))
        self.lblex1.pack()

        self.lblex2 = Label(frame, text=u"任选课为：" + u"，".join(EXCLUDE2))
        self.lblex2.pack()


def getStuName():
    html = rq.get('http://jwxt.bupt.edu.cn/menu/s_top.jsp',cookies=COOKIES).text
    soup = BeautifulSoup(html)
    name = soup.select('a[onclick="logout()"]')[0].previous_sibling.strip()
    return name.split(u'\xa0')[1]

def get_all_score(cookies):
    ret = []
    r = rq.get('http://jwxt.bupt.edu.cn/gradeLnAllAction.do?type=ln&oper=fainfo', cookies=cookies)
    soup = BeautifulSoup(r.text)
    rows = soup.select('#user')[0].find_all('tr')
    for cnt, row in enumerate(rows):
        if cnt != 0:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            d = {"id":cols[0], "id2":cols[1], "name":cols[2], "eng_name":cols[3], "rank":cols[4], "property":cols[5], "score":cols[6]}
            if d["score"] == "":
                d["score"] = "-1"
            ret.append(d)
    return ret
 

def get_score(cookies):
    ret = []
    r = rq.get('http://jwxt.bupt.edu.cn/gradeLnAllAction.do?type=ln&oper=fainfo', cookies=cookies)
    soup = BeautifulSoup(r.text)
    print r.text
    table_body = soup.select('#user')[0].find('thead')
    rows = table_body.find_all('tr')
    for cnt, row in enumerate(rows):
        if cnt != 0:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            d = {"id":cols[0], "id2":cols[1], "name":cols[2], "eng_name":cols[3], "rank":cols[4], "property":cols[5], "score":cols[6]}
            if d["score"] == "":
                d["score"] = "-1"
            ret.append(d)
    return ret

def cal_avg_score(cookies):
    global EXCLUDE1
    global EXCLUDE2
    scores = get_all_score(cookies)
    sum_score = 0
    rank = 0
    for score in scores:
        if score['score'] != '-1' and score['property'] != u'任选':
            try:
                sum_score += (float(score['score']) * float(score['rank']))
                rank += float(score['rank'])
            except:
                print u'成绩非数字：', score['name']
                EXCLUDE1.append(score['name'])
        else:
            print u'任选课：', score['name']
            EXCLUDE2.append(score['name'])
    if sum_score == 0:
        avg_score = 0
    else:
        avg_score = sum_score / rank
    return avg_score





root = Tk()
root.title(u"加权平均成绩计算器")
# width = 500
# height = 500
# xoffset = 100
# yoffset = 100
# root.geometry("%dx%d%+d%+d" % (width, height, xoffset, yoffset))
LoginRoot = Toplevel()
LoginPanel = makeLoginPanel(LoginRoot)
def callback(event):
    global LOGIN
    print('callback function')
    if LOGIN:
        MainPanel = makeMainPanel(root)
        root.deiconify()
        LoginRoot.unbind("<Destroy>",TopDestroy)
    else:
        root.destroy()
root.withdraw()
TopDestroy = LoginRoot.bind("<Destroy>",callback)
root.mainloop()
