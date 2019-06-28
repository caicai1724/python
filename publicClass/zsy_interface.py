#!python3
import logging
import sys
import time
import bs4
import requests
import json
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import MyBaseFun

# 知心慧学学管端 登录接口
# 返回user内的字典
def zsy_login(userName, userPassword):
    loginUrl = 'http://zsyapi.zhixinhuixue.com/coachio/iointerface_v2/login'
    data = {
        'userName': userName,
        'userPassword': userPassword,
        'version': '1.8.3',
        'testFlag': 0,
        'reUploadPrompt': 1
    }
    result = MyBaseFun.GetSoupByParams(loginUrl, data, 'JSON', '', '')
    if 'success' in result:
        if result['success'] == 1:
            return result['object']['user']
        else:
            return {'error': result['message']}
    return {'error': '登录失败：未知错误'}

# 知心慧学学管端 打印试卷查询接口
# 返回第一页的考试信息的字典列表
def zsy_print(session, pageNum):
    examList = []
    printUrl = 'http://zsyas2.zhixinhuixue.com/index.php/print/index/username/'\
               +session['userName']+'/time/'+str(session['time'])+'/sig/'+session['sig']+'/sessionid/'+session['sessionId']+ '/page/' + str(pageNum)
    res = MyBaseFun.GetRes(printUrl)
    result = bs4.BeautifulSoup(res.text, 'html.parser')
    examElems = result.select('table#dynamic-table tbody tr')
    if examElems:
        for examElem in examElems:
            examDir = {}
            if '【New】' in examElem.select('td')[0].getText():
                examDir['isNew'] = '【New】'
            else:
                examDir['isNew'] = ''
            examDir['examName'] = examElem.select('td')[0].getText().replace('【New】','').strip()
            examDir['examId'] = examElem.select('td img')[0].get('examid')
            examDir['examType'] = examElem.select('td')[2].getText().strip()
            examDir['gradeName'] = examElem.select('td')[3].getText().strip()
            examDir['createDay'] = examElem.select('td')[4].getText().strip()
            examDir['examDay'] = examElem.select('td')[5].getText().strip()
            examDir['examFlag'] = examElem.select('td')[7].getText().strip()
            examList.append(examDir)
    cookieJson = json.dumps(requests.utils.dict_from_cookiejar(res.cookies))
    return examList, cookieJson

# 知心慧学学管端 发送或取消标注接口
# type:'send','发送标注';'cancel','取消标注'
# status:
def zsy_sendlabeltask(examId, examName, sendType, status, cookiesJson):
    labelTaskUrl = 'http://zsyas2.zhixinhuixue.com/index.php/print/sendlabeltask'
    data = {
        'examId': examId,
        'examName': examName,
        'createTime': int(time.time()),
        'type': sendType,
        'status': status
    }
    hearders = {
        'Content-Type':'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
    }
    cookies = requests.utils.cookiejar_from_dict(json.loads(cookiesJson), cookiejar=None, overwrite=True)
    result = MyBaseFun.PostSoupByParams(labelTaskUrl, data, 'JSON', cookies, hearders)
    if 'success' in result:
        return result['message']
    return '发送标注失败'

def zsy_export(cookiesJson, pageNum):
    examList = []
    exportUrl = 'http://zsyas2.zhixinhuixue.com/index.php/export/index/page/' + str(pageNum)
    cookies = requests.utils.cookiejar_from_dict(json.loads(cookiesJson), cookiejar=None, overwrite=True)
    noStarchSoup = MyBaseFun.GetSoupByParams(exportUrl, '', 'HTML', cookies,'')
    examElems = noStarchSoup.select('table#dynamic-table tbody tr')
    if examElems:
        for examElem in examElems:
            examDir = {}
            if '【New】' in examElem.select('td')[0].getText():
                examDir['isNew'] = '【New】'
            else:
                examDir['isNew'] = ''
            examDir['examName'] = examElem.select('td')[0].getText().replace('【New】','').strip()
            examDir['examType'] = examElem.select('td')[1].getText().strip()
            examDir['examClass'] = examElem.select('td')[2].getText().strip()
            examDir['examId'] = examElem.select('td a[exam_id]')[0].get('exam_id')
            examList.append(examDir)
    return examList

# 知心慧学学管端 下载excel或word报表
def zsy_ajaxDown(cookiesJson, data):
    ajaxDownUrl = 'http://zsyas2.zhixinhuixue.com/index.php/export/ajax_down'
    hearders = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
    }
    cookies = requests.utils.cookiejar_from_dict(json.loads(cookiesJson), cookiejar=None, overwrite=True)
    result = MyBaseFun.PostSoupByParams(ajaxDownUrl, data, 'JSON', cookies, hearders)
    if 'result' in result:
        return result['result']

# 通过认证进入数据库登录页面
def zsy_author():
    result = MyBaseFun.GetSoupAuth('http://zsytls.zhixinhuixue.com/pma', 'zsy', r'B8YU23%dE&Ki(@Nm')
    tokenElem = result.select('input[name="token"]')
    phpMyAdminElem = result.select('input[name="phpMyAdmin"]')
    token = tokenElem[0].get('value')
    phpMyAdmin = phpMyAdminElem[0].get('value')
    return token, phpMyAdmin

# 登录数据库
def zsy_loginDB(serverIP):
    token, phpMyAdmin = zsy_author()
    data = {
        'pma_servername': serverIP,
        'pma_username': 'cy',
        'pma_password': 'J2rrdH27zcY65rAK',
        'server': 1,
        'token': token
    }
    headers = {
        'Authorization': 'Basic enN5OkI4WVUyMyVkRSZLaShATm0=',
        'Referer': 'http://zsytls.zhixinhuixue.com/pma',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    }
    result = MyBaseFun.PostSoupByParams('http://zsytls.zhixinhuixue.com/pma/index.php', data, 'text', '', headers)
    token = result.split('navigation.php?token=')[1].split('&amp')[0]
    phpMyAdmin = result.split('phpMyAdmin=')[1].split('"')[0]
    return token, phpMyAdmin

# 查询数据库SQL-GET方式
def zsy_queryDB(serverIP, url):
    token, phpMyAdmin = zsy_loginDB(serverIP)
    url = url + '&show_query=1&token=' + token
    headers = {
        'Authorization': 'Basic enN5OkI4WVUyMyVkRSZLaShATm0=',
        'Referer': 'http://zsytls.zhixinhuixue.com/pma/import.php',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    }
    cookies = {
        'pma_lang': 'zh-utf-8',
        'pma_charset': 'utf-8',
        'pma_collation_connection': 'utf8_general_ci',
        'pma_mcrypt_iv': 'ty2jHfWFmes%3D',
        'pma_theme': 'original',
        'pmaUser-1': '8RMWOfIHT7U%3D',
        'pmaServer-1': serverIP,
        'pma_navi_width': '200',
        'pmaPass-1': 'Rvd%2FoyoBn7q66mLcmCi3XQ%3D%3D',
        'pma_fontsize': '82%25',
        'phpMyAdmin': phpMyAdmin
    }
    result = MyBaseFun.GetSoupByParams(url, '', 'HTML', cookies, headers)
    return result

# 查询数据库SQL-POST方式
def zsy_queryDB_POST(serverIP, data):
    token, phpMyAdmin = zsy_loginDB(serverIP)
    url = 'http://zsytls.zhixinhuixue.com/pma/sql.php'
    data['token'] = token
    headers = {
        'Authorization': 'Basic enN5OkI4WVUyMyVkRSZLaShATm0=',
        'Referer': 'http://zsytls.zhixinhuixue.com/pma/import.php',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    }
    cookies = {
        'pma_lang': 'zh-utf-8',
        'pma_charset': 'utf-8',
        'pma_collation_connection': 'utf8_general_ci',
        'pma_mcrypt_iv': 'ty2jHfWFmes%3D',
        'pma_theme': 'original',
        'pmaUser-1': '8RMWOfIHT7U%3D',
        'pmaServer-1': serverIP,
        'pma_navi_width': '200',
        'pmaPass-1': 'Rvd%2FoyoBn7q66mLcmCi3XQ%3D%3D',
        'phpMyAdmin': phpMyAdmin
    }
    result = MyBaseFun.PostSoupByParams(url, data, 'HTML', cookies, headers)
    return result

# 查询学校的主机地址/库名/组ID
def zsy_dbname(schoolId):
    url = 'http://zsytls.zhixinhuixue.com/pma/import.php?db=zsy_business&table=database&sql_query=SELECT+%2A+FROM+%60database%60+WHERE+school_id%3D' + schoolId
    result = zsy_queryDB('10.19.106.131', url)
    IPstr = result.select('table tbody td')[4].getText().split(':')[0]
    dbstr = result.select('table tbody td')[7].getText()
    groupId = result.select('table tbody td')[9].getText()
    return IPstr, dbstr, groupId

# 根据考试名称条件查询范文的学生班级信息
def zsy_model_essay_by_examName(examName, IPstr, dbstr):
    url = 'http://zsytls.zhixinhuixue.com/pma/import.php?db=' + dbstr + '&table=student_info&' \
           'sql_query=select+si.realname%2Cc.class_name+from+student_info+si%2Cclass+c%2Cstudent_paper_topic_rs' \
           '+sptr%2Cstudent_model_essay+sme%2Cexam+e+where+si.student_id%3Dsptr.student_id+and+sptr.id%3Dsme.sptr_id' \
           '+and+sme.exam_group_id%3De.exam_group_id+and+e.name%3D"' + examName + '"+and+si.class_id%3Dc.class_id' \
           '+group+by+si.student_id'
    result = zsy_queryDB(IPstr, url)
    allnames = result.select('#table_results tbody tr')
    studentList = []
    for allname in allnames:
        student = {}
        student['realName'] = allname.select('td')[0].getText()
        student['className'] = allname.select('td')[1].getText()
        studentList.append(student)
    return studentList

# 根据exam_group_id查询范文的学生班级信息和范文图片
def zsy_model_essay_by_examGroupId(examGroupId, IPstr, dbstr, groupId):
    data = {
        'db': dbstr,
        'table': 'student_info',
        'sql_query': 'select si.realname,c.class_name,sptr.answer_url from student_info si,class c,'
                     'student_paper_topic_rs sptr,student_model_essay sme where si.student_id=sptr.student_id '
                     'and sptr.id=sme.sptr_id and sme.exam_group_id='+examGroupId+' and si.class_id=c.class_id',
        'goto': 'tbl_sql.php',
        'display_options_form': '1',
        'display_text': 'F',
        'display_binary': 'on',
        'display_binary_as_hex': 'on'
    }
    result = zsy_queryDB_POST(IPstr, data)
    allnames = result.select('#table_results tbody tr')
    studentList = []
    for allname in allnames:
        student = {}
        student['realName'] = allname.select('td')[0].getText()
        student['className'] = allname.select('td')[1].getText()
        student['imgUrl'] = 'http://zstatic'+groupId+'.zhixinhuixue.com' + allname.select('td')[2].getText()
        studentList.append(student)
    return studentList

# 查询本学期内有范文标识的考试列表
def zsy_examList_model(IPstr, dbstr):
    subjectDir = {'8': '英语', '9': '语文'}
    url = 'http://zsytls.zhixinhuixue.com/pma/import.php?db='+dbstr+'&table=exam&' \
           'sql_query=SELECT+e.exam_group_id,e.subject_id,e.name,from_unixtime(e.create_time)+from+exam+' \
           'e,student_model_essay+sme,semester+s+WHERE+e.exam_group_id=sme.exam_group_id+and+' \
           'e.semester_id=s.semester_id+and+s.status=1+group+by+e.exam_group_id'
    result = zsy_queryDB(IPstr, url)
    allElems = result.select('#table_results tbody tr')
    examList = []
    for allElem in allElems:
        exam = {}
        exam['examGroupId'] = allElem.select('td')[0].getText()
        subjectId = allElem.select('td')[1].getText()
        exam['subject'] = subjectDir[subjectId]
        exam['examName'] = allElem.select('td')[2].getText()
        exam['createTime'] = allElem.select('td')[3].getText()
        examList.append(exam)
    return examList

zsy_login('nccs','ncxxjszx')
