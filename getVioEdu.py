# -*- coding: utf8 -*-
import requests
import getpass
import threading
import os
import io
import time
import sqlite3
import json
from requests_toolbelt.utils import dump
import random
from random import randrange
import re
from difflib import SequenceMatcher
from requests_toolbelt.utils import dump
p = os.getcwd()
bd = os.path.join(p, r'udfn.db')
db_conn = sqlite3.connect(bd)
c = db_conn.cursor()
c.execute(
			"""
			CREATE TABLE if not exists category (
			catid TEXT,
            catname TEXT,
            cattype TEXT,
            semester TEXT
 			);
			"""
		)
c.execute(
			"""
			CREATE TABLE if not exists bode (
			bdid TEXT,
            bdname TEXT,
            rctype TEXT,
            catid TEXT,
            catname TEXT,
            cattype TEXT
 			);
			"""
		)
c.execute(
			"""
			CREATE TABLE if not exists ques (
			questionId TEXT,
            question_type TEXT,
            question_content TEXT,
            question_dapan TEXT,
            bdid TEXT
 			);
			"""
		)
c.execute(
			"""
			CREATE TABLE if not exists answers (
			answers_id TEXT,
            answers_text TEXT,
            questionId TEXT
 			);
			"""
		)
db_conn.commit()
c.execute("DELETE FROM category")
c.execute("DELETE FROM bode")
db_conn.commit()
def calratiotext(text1,text2):
    m = SequenceMatcher(None, text1, text2)
    x=m.ratio()
    return x
def getratio(realques):
    c = db_conn.cursor()
    sql2 = "SELECT question_content FROM ques"
    c.execute(sql2)
    alrow=c. fetchall()
    ce=0
    mans=''
    for a in alrow:
        dbques=a[0]
        c=calratiotext(realques,dbques)
        if (c>ce):
            ce=c
            mans=dbques
    return mans, ce
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  # cleantext = cleantext.replace("&nbsp;","")
  return cleantext
def getexamlist(catid,catname,cattype):
    if cattype=='category':
        burp0_url = "https://vio.edu.vn:443/graphql"
        burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/skill-list", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
        burp0_json={"operationName": "getSkillListQuery", "query": "query getSkillListQuery($idSubject: String, $idCategory: String, $grade: Int, $unit: Int, $useForMobile: Boolean) {\n  getSkillList(idSubject: $idSubject, idCategory: $idCategory, grade: $grade, unit: $unit, useForMobile: $useForMobile) {\n    _id\n    name\n    currentScore\n    canLearn\n    pastScore\n    isWeakness\n    order\n    recordType\n    isDemo\n    duration\n    numberOfQuestion\n    grade\n    thumbnails\n    media {\n      media\n      mediaType\n      mediaThumbnail\n      link\n      name\n      __typename\n    }\n    isCompleted\n    hasQuestion\n    topicFull {\n      _id\n      name\n      order\n      __typename\n    }\n    categoryFull {\n      _id\n      name\n      order\n      __typename\n    }\n    __typename\n  }\n}\n", "variables": {"grade": 4, "idCategory": catid, "idSubject": ""}}
        response=requests.post(burp0_url, headers=burp0_headers, json=burp0_json)
    elif cattype=='exam':
        burp0_url = "https://vio.edu.vn:443/graphql"
        burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/skill-list", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
        burp0_json={"operationName": "getExamTemplateListQuery", "query": "query getExamTemplateListQuery($page: Int!, $itemPerPage: Int!, $filter: ExamTemplateFilterType!) {\n  getListExamTemplate(page: $page, itemPerPage: $itemPerPage, filter: $filter) {\n    _id\n    name\n    grade\n    lastScore\n    behindSkill\n    isDemo\n    canLearn\n    numberOfQuestion\n    duration\n    skill {\n      id\n      text\n      __typename\n    }\n    __typename\n  }\n}\n", "variables": {"filter": {"grade": 4, "unit": [catid]}, "itemPerPage": 100, "page": 1}}
        response=requests.post(burp0_url, headers=burp0_headers, json=burp0_json)
    az=response.content
    az=az.decode("utf-8") 
    aj=json.loads(az)
    fname='getkq2.xml'
    with io.open(fname, "w", encoding="utf-8") as f:
        f.write(az)
        f.close()
    if cattype=='category':
        d=aj['data']['getSkillList']
    elif cattype=='exam':
        d=aj['data']['getListExamTemplate']
    val2=[]
    fre=[]
    for d1 in d:
        if cattype=='category':
            rctype=d1['recordType']
        elif cattype=='exam':
            rctype='EXAM'
        # if (rctype=='EXAM') or (rctype=='SKILL'):
        if (rctype=='EXAM'):
            bdid=d1['_id']
            fre.append(bdid)
            bdname=d1['name']
            info2=(bdid,bdname,rctype,catid,catname,cattype)
            val2.append(info2)
            # print(bdid)
    sql = "INSERT INTO bode (bdid,bdname,rctype, catid, catname, cattype) VALUES (?, ?, ?, ?, ?, ?)"
    c = db_conn.cursor()
    c.executemany(sql, val2)
    db_conn.commit()
    return fre

def getexamresult(bdid):
    burp0_url = "https://vio.edu.vn:443/graphql"
    burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/exam-log/"+bdid, "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
    burp0_json={"operationName": "getListExamLog", "query": "query getListExamLog($examTemplate: String) {\n  getExamLogList(examTemplate: $examTemplate) {\n    _id\n    score\n    exam {\n      name\n      examTemplateFull {\n        numberOfQuestion\n        __typename\n      }\n      __typename\n    }\n    template {\n      _id\n      name\n      __typename\n    }\n    numberCorrect\n    duration\n    createdTime\n    skillSummary {\n      skillText\n      percent\n      __typename\n    }\n    __typename\n  }\n}\n", "variables": {"examTemplate": bdid}}
    response=session.post(burp0_url, headers=burp0_headers, json=burp0_json)
    az=response.content
    az=az.decode("utf-8") 
    aj=json.loads(az)
    h=aj['data']['getExamLogList']
    for h1 in h:
        hid=h1['_id']
        burp0_url = "https://vio.edu.vn:443/graphql"
        burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/exam-log-detail/"+hid, "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
        burp0_json={"operationName": "getExamLogDetail", "query": "query getExamLogDetail($logID: String) {\n  getExamLogDetail(logID: $logID) {\n    score\n    scoreOrigin\n    unit\n    numberCorrect\n    numberQuestion\n    duration\n    isFree\n    showGiaiThich\n    skillSummary {\n      skillId\n      skillText\n      percent\n      __typename\n    }\n    examLog {\n      _id\n      explanation {\n        text\n        order\n        __typename\n      }\n      isCorrect\n      question_type\n      questionId\n      question_index\n      question_content\n      user_answer\n      numberColumn\n      numberRow\n      totalPart\n      question_answers {\n        _id\n        id\n        text\n        answerType\n        position\n        order\n        partType\n        listSubAnswer {\n          _id\n          textContent\n          __typename\n        }\n        __typename\n      }\n      score\n      scoreOrigin\n      __typename\n    }\n    __typename\n  }\n}\n", "variables": {"logID": hid}}
        response=session.post(burp0_url, headers=burp0_headers, json=burp0_json)
        az=response.content
        az=az.decode("utf-8") 
        aj=json.loads(az)
        fname='getkq.xml'
        with io.open(fname, "w", encoding="utf-8") as f:
            f.write(az)
            f.close()
        da=aj['data']['getExamLogDetail']['examLog']
        val3=[]
        val4=[]
        for da1 in da:
            dapan=da1['explanation'][0]['text']
            # print(dapan)
            if "Đáp án:" in dapan: 
                dapan1=dapan.split("Đáp án:")[1]
            else:
                dapan1=dapan
            question_dapan=cleanhtml(dapan1)
            question_content=da1['question_content']
            question_type=da1['question_type']
            questionId=da1['questionId']
            c = db_conn.cursor()
            sql = "SELECT COUNT(*) FROM ques where questionId = ?"
            ic = (questionId, )
            c.execute(sql,ic)
            result=c.fetchone()
            number_of_rows=result[0]
            if number_of_rows==0:
                question_index=da1['question_index']
                print(question_type)
                print(question_index)
                question_content=cleanhtml(question_content)
                info3=(questionId,question_type,question_content,question_dapan,bdid)
                val3.append(info3)
                if question_type!=10:
                    print(question_dapan)
                    # print(questionId)
                    # print(question_type)
                    # print(question_content)
                question_answers=da1['question_answers']
                for q1 in question_answers:
                    answers_id=q1['_id']
                    answers_text=q1['text']
                    answers_text=cleanhtml(answers_text)
                    answers_text=answers_text.replace('\\','')
                    info4=(answers_id,answers_text,questionId)
                    val4.append(info4)
                    # ans=result.replace("\\", "")
                    # if question_type==1:
                        # print(ans)
        sql = "INSERT INTO ques (questionId,question_type,question_content,question_dapan,bdid) VALUES (?, ?, ?, ?, ?)"
        c = db_conn.cursor()
        c.executemany(sql, val3)
        sql = "INSERT INTO answers (answers_id,answers_text,questionId) VALUES (?, ?, ?)"
        c = db_conn.cursor()
        c.executemany(sql, val4)
        db_conn.commit()

def lamtn(bdid):
        burp0_url = "https://vio.edu.vn:443/graphql"
        burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/skill-test/"+bdid, "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
        burp0_json={"operationName": "getExam", "query": "query getExam($idTemplate: String) {\n  getExamByExamTemplateID(templateID: $idTemplate) {\n    _id\n    isDemo\n    canExam\n    examTemplateFull {\n      name\n      duration\n      grade\n      numberOfQuestion\n      __typename\n    }\n    examInformation {\n      skillName\n      question_number\n      __typename\n    }\n    questions {\n      _id\n      content\n      questionId\n      childrenQuestions {\n        _id\n        content\n        q_index\n        q_type\n        isConsider\n        numberRow\n        numberColumn\n        styleAnswer\n        autoConvert\n        answerColumnNo\n        isConsider\n        score\n        answers {\n          _id\n          id\n          text\n          subText\n          selected\n          answerType\n          partType\n          position\n          order\n          inputLength\n          __typename\n        }\n        __typename\n      }\n      q_index\n      q_type\n      isConsider\n      numberRow\n      numberColumn\n      totalPart\n      colorPart\n      styleAnswer\n      autoConvert\n      answerColumnNo\n      isConsider\n      score\n      audio {\n        content\n        explanation\n        __typename\n      }\n      rightMatching {\n        _id\n        right_answer_id: id\n        textContent\n        __typename\n      }\n      leftMatching {\n        id\n        textContent\n        __typename\n      }\n      listSubAnswer {\n        _id\n        textContent\n        __typename\n      }\n      answers {\n        _id\n        id\n        text\n        subText\n        selected\n        answerType\n        partType\n        position\n        order\n        inputLength\n        listSubAnswer {\n          _id\n          textContent\n          __typename\n        }\n        __typename\n      }\n      textDropdownAnswers {\n        _id\n        list {\n          value: _id\n          label: text\n          __typename\n        }\n        order\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n", "variables": {"idTemplate": bdid}}
        response=session.post(burp0_url, headers=burp0_headers, json=burp0_json)
        az=response.content
        az=az.decode("utf-8") 
        aj=json.loads(az)
        # print(aj)
        fname='getkq1.xml'
        with io.open(fname, "w", encoding="utf-8") as f:
            f.write(az)
            f.close()
        examid=aj['data']['getExamByExamTemplateID']['_id']
        examques=aj['data']['getExamByExamTemplateID']['questions']
        datae=[] 
        for examq in examques:
            exq=examq['content']
            questionId=examq['questionId']
            examf=examq

            q_index=examq['q_index']
            q_type=examq['q_type']
            # print(q_index)
            # print(q_type)
            exq=cleanhtml(exq)
            mans, ce=getratio(exq)
            if (ce>0.90):
                sql = "SELECT * FROM ques where question_content = ?"
                ic = (mans, )
                c.execute(sql,ic)
                row=c.fetchall()
                data=row
                andb=data[0][3]
            else:
                andb=''
            
            andb=andb.replace(',','')
            andb=andb.replace('.','')
            andb=andb.replace('\\','')
            andb=andb.replace('(','')
            andb=andb.replace(')','')
            andb=andb.replace(';','')
            andb=andb.replace('&nbsp',' ')
            andb=andb.strip()
            andb2=andb.splitlines()
            andb2l=len(andb2)
            question_answers=examq['answers']
            
            an2=[0]*andb2l
            ant2=[0]*andb2l
            ratior2=[0]*andb2l
            an=""
            ant=""
            ratior=0
            i=0
            for q1 in question_answers:
                try:
                    del examf['answers'][i]['__typename']
                    del examf['answers'][i]['inputLength']
                    del examf['answers'][i]['subText']
                except KeyError:
                    pass
                answers_id=q1['_id']
                answers_text=q1['text']
                
                if q_type=='1' or q_type=='2':
                    examf['answers'][i]['selected']=False
                    answers_text=cleanhtml(answers_text)
                    answers_text=answers_text.replace('\\','')
                    answers_text=answers_text.replace('(','')
                    answers_text=answers_text.replace(')','')
                    answers_text=answers_text.replace('.','')
                    answers_text=answers_text.replace(';','')
                    answers_text=answers_text.replace(',','')
                    answers_text=answers_text.replace('&nbsp',' ')
                    answers_text=answers_text.strip()
                    # print(answers_text)
                    if q_type=='1':
                        ratio=calratiotext(andb,answers_text)
                        if ratio>ratior:
                            an=answers_id
                            ant=answers_text
                            ratior=ratio
                    else: 
                        dbc=0
                        for andb2x in andb2:
                            ratio=calratiotext(andb2x,answers_text)
                            if ratio>ratior2[dbc]:
                                an2[dbc]=answers_id
                                ant2[dbc]=answers_text
                                ratior2[dbc]=ratio
                            dbc+=1
                if q_type=='3':
                    examf['answers'][i]['selected']=False
                    # print(andb2)
                    if andb2l>i:
                        examf['answers'][i]['text']=andb2[i]
                    else:
                        x=randrange(999999)
                        examf['answers'][i]['text']=x
                i+=1  
            
           
            if q_type=='7':
                textDropdownAnswers=examq['textDropdownAnswers']
                # print(textDropdownAnswers)
                selected={}
                selected['selected']=False
                ct=0
                for t in textDropdownAnswers:
                    tlist=t['list']
                    ctt=0
                    try:
                        del examf['textDropdownAnswers'][ct]['__typename']
                    except KeyError:
                        pass
                    ratior=0
                    val=''
                    ind=0
                    for tt in tlist:
                        try:
                            del examf['textDropdownAnswers'][ct]['list'][ctt]['__typename']
                        except KeyError:
                            pass
                        examf['textDropdownAnswers'][ct]['list'][ctt].update(selected) 
                        if andb2l>ct:
                            andb2x=andb2[ct]
                            answers_text=examf['textDropdownAnswers'][ct]['list'][ctt]['label']
                            ratio=calratiotext(andb2x,answers_text)
                            if ratio>ratior:
                                ind=ctt
                                val=answers_text
                                ratior=ratio
                        ctt+=1
                    examf['textDropdownAnswers'][ct]['list'][ind]['selected']=True
                    ct+=1

            if q_type=='6':
                print(q_index)
                print(examq)
                rightMatching=examq['rightMatching']
                leftMatching=examq['leftMatching']
                # print(rightMatching)
                # print(leftMatching)
                # print(question_answers)
                listAnswerDrop=[]
                for q1 in question_answers:
                    # print(q1)
                    lad={}
                    rm=q1['_id']
                    rmm=next((i for i, item in enumerate(rightMatching) if item["_id"] == rm), None)
                    iddrag=rightMatching[rmm]['right_answer_id']
                    
                    lm=q1['id']
                    lad['iddrag']=str(iddrag)
                    lad['position']=lm
                    listAnswerDrop.append(lad)
                    # print (lad)
                ladd={}
                ladd['listAnswerDrop']=listAnswerDrop
                print(listAnswerDrop)
                examf.update(ladd)

            if q_type=='1':
                x=randrange(i)
                if ratior>0.1:
                    dt=next((i for i, item in enumerate(question_answers) if item["_id"] == an), None)
                    examf['answers'][dt]['selected']=True
                else:
                    examf['answers'][x]['selected']=True
                
            
            if q_type=='2':
                x=randrange(i)
                k=0
                for an in an2:
                   ratior=ratior2[k]
                   if ratior>0.1:
                        dt=next((i for i, item in enumerate(question_answers) if item["_id"] == an), None)
                        examf['answers'][dt]['selected']=True
                   else:
                        examf['answers'][x]['selected']=True
                   k+=1
            if q_type!='10':
                try:
                    del examf['questionId']
                    del examf['styleAnswer']
                    del examf['answerColumnNo']
                    del examf['audio']
                    del examf['rightMatching']
                    del examf['leftMatching']
                    del examf['__typename']
                except KeyError:
                    pass
            # examfo = [classthing(s) for s in examf]
            datae.append(examf)
         
        # dataex=json.dumps(datae)
        # print(datae)
        xr=randrange(50,87)
        burp0_url = "https://vio.edu.vn:443/graphql"
        burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/skill-test/"+bdid, "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
        burp0_json={"operationName": "SubmitExam", "query": "mutation SubmitExam($templateID: String, $examID: String, $trialTestID: String, $duration: Int, $examSubmit: [AnswerInExamResultSubmit]) {\n  checkResultExam(templateID: $templateID, examID: $examID, trialTestID: $trialTestID, duration: $duration, examSubmit: $examSubmit) {\n    _id\n    score\n    numberCorrect\n    numberQuestion\n    numberEssayQuestion\n    duration\n    isFree\n    unit\n    showGiaiThich\n    isEntranceExam\n    skillSummary {\n      skillId\n      skillText\n      percent\n      __typename\n    }\n    generalSummary {\n      practice_score\n      skill_id\n      skill_name\n      exam_score\n      __typename\n    }\n    examLog {\n      explanation {\n        text\n        order\n        __typename\n      }\n      isCorrect\n      childrenQuestions {\n        questionId\n        score\n        scoreOrigin\n        __typename\n      }\n      questionId\n      question_type\n      question_index\n      question_content\n      user_answer\n      numberColumn\n      autoConvert\n      numberRow\n      totalPart\n      question_answers {\n        _id\n        id\n        text\n        subText\n        answerType\n        position\n        order\n        partType\n        listSubAnswer {\n          _id\n          textContent\n          __typename\n        }\n        __typename\n      }\n      score\n      scoreOrigin\n      scoreMixQuestion\n      __typename\n    }\n    __typename\n  }\n}\n", "variables": {"duration": xr, "examID": examid, "examSubmit": datae, "templateID": bdid, "trialTestID": ""}}
        response=session.post(burp0_url, headers=burp0_headers, json=burp0_json)      
        az=response.content
        az=az.decode("utf-8") 
        data = dump.dump_all(response)
        aj=(data.decode('utf-8'))
        # print(az)
        fname='getkqe.xml'
        with io.open(fname, "w", encoding="utf-8") as f:
            f.write(aj)
            f.close()
        fname='getkqe2.xml'
        with io.open(fname, "w", encoding="utf-8") as f:
            f.write(az)
            f.close()
        
        
   

session = requests.session()

burp0_url = "https://vio.edu.vn:443/login"
burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "Accept": "application/json, text/plain, */*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "Content-Type": "application/json;charset=UTF-8", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/login", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
burp0_json={"password": "PASSWORD", "username": "USERNAME"}
response=session.post(burp0_url, headers=burp0_headers, json=burp0_json)
az=response.content
az=az.decode("utf-8") 

if az=="Unauthorized":
    print("SAI USER/PASS. KIEM TRA LAI")
    exit()
semester=1
while semester<=2:
    burp0_url = "https://vio.edu.vn:443/graphql"
    burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "accept": "*/*", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "content-type": "application/json", "Origin": "https://vio.edu.vn", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://vio.edu.vn/skill-list", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
    burp0_json={"operationName": "getListTopicSkill", "query": "query getListTopicSkill($grade: Int, $subjectId: String, $semester: Int) {\n  getListTopicSkill(grade: $grade, subjectId: $subjectId, semester: $semester)\n}\n", "variables": {"grade": 4, "semester": semester, "subjectId": ""}}
    response=session.post(burp0_url, headers=burp0_headers, json=burp0_json)
    az=response.content
    az=az.decode("utf-8") 
    aj=json.loads(az)
    s=aj['data']['getListTopicSkill']['listCategory']
    # print(s)
    val=[]
    for s1 in s:
        catid=s1['_id']
        catname=s1['name']
        cattype=s1['type']
        # print(catname)
        examlist=getexamlist(catid,catname,cattype)
        # print(examlist)
        for el in examlist:
            # print(el)
            lamtn(el)
            getexamresult(el)
        info=(catid,catname,cattype,semester)
        val.append(info)
    sql = "INSERT INTO category (catid, catname, cattype, semester) VALUES (?, ?, ?, ?)"
    c = db_conn.cursor()
    c.executemany(sql, val)
    db_conn.commit()
    semester+=1









burp0_url = "https://vio.edu.vn:443/logout"
burp0_cookies = {"lang": "en-US", "_dvp": "0:knpt17al:pSJhCJ6EIjMrO~n8sgpK~YkoAG_gddlO", "_ga": "GA1.3.1202064766.1618909695", "_ga": "GA1.1.1202064766.1618909695", "_fbp": "fb.2.1618909695831.576348930", "_gid": "GA1.3.2058372281.1619062930", "_gid": "GA1.1.2058372281.1619062930", "_dvs": "0:knsc9k9d:rfmZRZJ8YF71B0Fc~YwMsg1oGB7tq5WA", "connect.sid": "s%3AIjxYWCFrd1_yTLTsyi2CrczUKQXpqinf.e718QiMXMVTGIU0JqE2PwhbMJs228CkzP5US%2Bv0Dn70", "_gat": "1", "_gat_gtag_UA_188276260_1": "1"}
burp0_headers = {"Connection": "close", "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"", "sec-ch-ua-mobile": "?0", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://vio.edu.vn/skill-list", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
session.get(burp0_url, headers=burp0_headers)