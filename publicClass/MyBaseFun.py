#!python3
import pymysql
import time
import os
import requests
import bs4
import traceback
import logging
import datetime
import re
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
from requests.auth import HTTPBasicAuth

def GetRes(url, timeout=10, trynum=5):
    t = 0
    while t < trynum:
        try:
            res = requests.get(url, timeout=timeout)
            break
        except requests.exceptions.ConnectionError:
            logging.info("ConnectionError,url:%s", url)
            t = t + 1
            time.sleep(5)
        except requests.exceptions.ChunkedEncodingError:
            logging.info("ChunkedEncodingError,url:%s", url)
            t = t + 1
            time.sleep(5)
        except:
            logging.info("Unfortunitely -- An Unknow Error Happened,url:%s", url)
            t = t + 1
            time.sleep(5)
    res.raise_for_status()  # 如果返回不是200，则抛出异常
    return res

# 访问网页获取html Soup数据
# url:待访问的页面
# timeout:等待超时的时间，默认10秒
# trynum:超时后尝试重复几次访问，默认5次
def GetSoup(url,timeout=10,trynum=5):
    res = GetRes(url, timeout, trynum)
    # print(res.apparent_encoding)
    # res.encoding: 从HTTP header中猜测的响应内容编码方式，不规范网页使用默认的 ISO-8859-1
    if res.encoding == 'ISO-8859-1':
        # encode方法：将字符串转化为你所想要的编码格式，比如utf-8等
        tmp = res.text.encode(res.encoding)
        print(res.apparent_encoding)
        # decode方法：以指定的编码格式解码字符串
        # apparent_encoding：从内容中分析出的响应内容编码方式
        if res.apparent_encoding == 'Windows-1254':
            r = tmp.decode('utf-8')
        else:
            r = tmp.decode(res.apparent_encoding, errors='ignore')
    else:
        r = res.text
    noStarchSoup = bs4.BeautifulSoup(r, 'html.parser')
    return noStarchSoup

# 带参数的访问网页，返回HTML或JSON格式
# url:待访问的页面
# timeout:等待超时的时间，默认10秒
# trynum:超时后尝试重复几次访问，默认5次
# paramData:参数
# type:'HTML(返回HTML格式),JSON(返回JSON格式)'
def GetSoupByParams(url, paramData, type, cookies, headers, timeout=10,trynum=5):
    t = 0
    while t < trynum:
        try:
            res = requests.get(url, params=paramData, cookies=cookies, headers=headers, timeout=timeout)
            break
        except requests.exceptions.ConnectionError:
            print("ConnectionError,url:"+url)
            t = t + 1
            time.sleep(5)
        except requests.exceptions.ChunkedEncodingError:
            print("ChunkedEncodingError,url:"+url)
            t = t + 1
            time.sleep(5)
        except:
            print("Unfortunitely -- An Unknow Error Happened,url:"+url)
            t = t + 1
            time.sleep(5)
    res.raise_for_status()  # 如果返回不是200，则抛出异常
    if res.encoding == 'ISO-8859-1':
        # encode方法：将字符串转化为你所想要的编码格式，比如utf-8等
        tmp = res.text.encode(res.encoding)
        print(res.apparent_encoding)
        # decode方法：以指定的编码格式解码字符串
        # apparent_encoding：从内容中分析出的响应内容编码方式
        if res.apparent_encoding == 'Windows-1254':
            r = tmp.decode('utf-8')
        else:
            r = tmp.decode(res.apparent_encoding, errors='ignore')
    else:
        r = res.text
    if type == 'HTML':
        noStarchSoup = bs4.BeautifulSoup(r, 'html.parser')
        return noStarchSoup
    elif type == 'JSON':
        try:
            return json.loads(r)
        except ValueError:
            return ''
        
def PostSoupByParams(url, paramData, type, cookies, headers, timeout=20,trynum=5):
    t = 0
    while t < trynum:
        try:
            res = requests.post(url, data=paramData, cookies=cookies, headers=headers, timeout=timeout)
            break
        except requests.exceptions.ConnectionError:
            logging.info("ConnectionError,url:%s", url)
            t = t + 1
            time.sleep(5)
        except requests.exceptions.ChunkedEncodingError:
            logging.info("ChunkedEncodingError,url:%s", url)
            t = t + 1
            time.sleep(5)
        except:
            logging.info("Unfortunitely -- An Unknow Error Happened,url:%s", url)
            t = t + 1
            time.sleep(5)
    res.raise_for_status()  # 如果返回不是200，则抛出异常
    if res.encoding == 'ISO-8859-1':
        # encode方法：将字符串转化为你所想要的编码格式，比如utf-8等
        tmp = res.text.encode(res.encoding)
        print(res.apparent_encoding)
        # decode方法：以指定的编码格式解码字符串
        # apparent_encoding：从内容中分析出的响应内容编码方式
        if res.apparent_encoding == 'Windows-1254':
            r = tmp.decode('utf-8')
        else:
            r = tmp.decode(res.apparent_encoding, errors='ignore')
    else:
        r = res.text
    if type == 'HTML':
        noStarchSoup = bs4.BeautifulSoup(r, 'html.parser')
        return noStarchSoup
    elif type == 'JSON':
        try:
            return json.loads(r)
        except ValueError:
            return ''
    elif type == 'text':
        return r

# selenium模块下，获取页面所有加载html数据,所见即所得
def GetSeleniumSoup(url, driverPath):
    if 'chromedriver' in driverPath:
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        driver = webdriver.Chrome(options=opt,executable_path=driverPath)
    elif 'geckodriver' in driverPath:
        opt = webdriver.firefox.Options()
        opt.add_argument('-headless')
        driver = webdriver.Firefox(executable_path=driverPath, firefox_options=opt)
    driver.set_page_load_timeout(120)
    t = 0
    while t < 5:
        try:
            driver.get(url)
            if driver.title.startswith('500'):
                logging.info("500 error,url:%s", url)
                t = t + 1
                time.sleep(5)
                continue
            else:
                break
        except:
            logging.info("Unfortunitely -- An Unknow Error Happened,url:%s", url)
            t = t + 1
            time.sleep(5)
    noStarchSoup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    return noStarchSoup

def GetSeleniumSoupScroll(url, driverPath):
    if 'chromedriver' in driverPath:
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        driver = webdriver.Chrome(options=opt, executable_path=driverPath)
    elif 'geckodriver' in driverPath:
        opt = webdriver.firefox.Options()
        opt.add_argument('-headless')
        driver = webdriver.Firefox(executable_path=driverPath, firefox_options=opt)
    driver.set_page_load_timeout(120)
    t = 0
    while t < 5:
        try:
            driver.get(url)
            if driver.title.startswith('500'):
                logging.info("500 error,url:%s", url)
                continue
            else:
                break
        except:
            logging.info("Unfortunitely -- An Unknow Error Happened,url:%s", url)
            t = t + 1
            time.sleep(5)
    # 下拉页面到最低，如果“已经到底”的属性还被隐藏中，则继续下拉页面
    while 1:
        moreLoad = driver.find_element_by_xpath(".//*[@data-role='finished']")
        if moreLoad.get_attribute('style'):
            logging.debug('有下一页：%s',moreLoad.get_attribute('style'))
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        else:
            break
    noStarchSoup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    return noStarchSoup

# selenium模块下，获取页面所有加载html数据,点击某个页面元素
def GetSeleniumSoupClick(url, driverPath, clickClassName):
    if 'chromedriver' in driverPath:
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        driver = webdriver.Chrome(options=opt,executable_path=driverPath)
    elif 'geckodriver' in driverPath:
        opt = webdriver.firefox.Options()
        opt.add_argument('-headless')
        driver = webdriver.Firefox(executable_path=driverPath, firefox_options=opt)
    driver.set_page_load_timeout(120)
    t = 0
    while t < 5:
        try:
            driver.get(url)
            break
        except:
            logging.info("Unfortunitely -- An Unknow Error Happened,url:%s", url)
            t = t + 1
            time.sleep(5)
    elemClick = driver.find_elements_by_class_name(clickClassName)[1]
    elemClick.click()
    time.sleep(2)
    noStarchSoup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    return noStarchSoup

# 下载图片
# url:待访问的图片链接
# timeout:等待超时的时间，默认10秒
# trynum:超时后尝试重复几次访问，默认5次
def GetSaveImg(imgUrl,uploadImgDir,timeout=10,trynum=5):
    t = 0
    while t < trynum:
        try:
            picRes = requests.get(imgUrl, timeout=timeout)
            break
        except requests.exceptions.ConnectionError:
            logging.info("ConnectionError,url:%s", imgUrl)
            t = t + 1
            time.sleep(5)
        except requests.exceptions.ChunkedEncodingError:
            logging.info("ChunkedEncodingError,url:%s", imgUrl)
            t = t + 1
            time.sleep(5)
        except:
            logging.info("Unfortunitely -- An Unknow Error Happened,url:%s", imgUrl)
            t = t + 1
            time.sleep(5)
    # res.raise_for_status()  # 如果返回不是200，则抛出异常
    fileName = os.path.basename(imgUrl).split('?')[0].replace('=','')
    filePath = os.path.join(uploadImgDir, fileName)
    fp = open(filePath, 'wb')
    fp.write(picRes.content)
    fp.close()
    return filePath

# 读取配置文件
def get_cont_conf(conf_file_name):
    configDict = {}
    configFile = open(conf_file_name, encoding='UTF-8')
    lines = configFile.readlines()
    for line in lines:
        if '=' in line:
            conKey = line.split('=',1)[0].strip(' ')
            conValue = line.split('=',1)[1].strip('\n').strip(' ').strip('\'').strip('\"')
            configDict[conKey] = conValue
    return configDict

# 获取日期，返回标准格式，201X-XX-XX
def GetDateStr(dateStr):
    yearTup = ('2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024')
    if '月' in dateStr:
        m = dateStr.split('月')[0][-2:]
        d = dateStr.split('日')[0][-2:]
        if '年' in dateStr:
            y = dateStr.split('年')[0][-4:]
        else:
            y = yearNow
        return (y + '-' + m + '-' + d)
    else:
        patternAll = re.compile('20\d\d-\d\d-\d\d')
        patternPart = re.compile('\d\d-\d\d')
        tmpDate = patternAll.findall(dateStr)
        if tmpDate:
            return tmpDate[0]
        tmpDate = patternPart.findall(dateStr)
        if tmpDate:
            return str(datetime.datetime.now().year) + '-' + tmpDate[0]

# 获取到时间戳
def GetUpdate(elems_str, dateFlag, dateStatus):
    dateElems = elems_str.select(dateFlag)
    for dateElem in dateElems:
        logging.debug("dateElem:%s,dateFlag:%s",dateElem,dateFlag)
        # 时间戳在标签内
        if dateStatus == 2:
            pattern = re.compile('\d{10}')
            updateTmp = pattern.findall(str(dateElem))[0]
            return updateTmp
        if '[' in dateFlag:
            datePro = dateFlag.split('[')[1].split(']')[0]
            return (float(dateElem.get(datePro)[:-3]))
        else:
            for dateStr in dateElem.getText().split(' '):
                if ('-' in dateStr) or ('月' in dateStr and '日' in dateStr):
                    updateStr = GetDateStr(dateStr)
                    return (time.mktime(time.strptime(updateStr, "%Y-%m-%d")))
                elif '今天' in dateStr:
                    return GetCurTime()
                elif '昨天' in dateStr:
                    return GetCurTime() - 86400

# 获取当天0点时间戳
def GetCurTime():
    #当天零点时间戳
    cur_time=time.time()
    return cur_time - cur_time%86400 + time.timezone

# 根据站点获取完整的URL
def GetComURL(sourceUrl,url):
    if url.startswith('http'):
        return url
    else:
        urlList = sourceUrl.split('/')
        if url.startswith('../../'):
            tmpUrl = "/".join(urlList[:-3])
            return tmpUrl + url.replace('../../','/')
        elif url.startswith('../'):
            tmpUrl = "/".join(urlList[:-2])
            return tmpUrl + url.strip('.')
        elif url.startswith('./'):
            tmpUrl = "/".join(urlList[:-1])
            return tmpUrl + url.strip('.')
        elif url.startswith('//'):
            return 'http:' + url
        elif url.startswith('/'):
            tmpUrl = "/".join(urlList[:3])
            return tmpUrl + url
        else:
            tmpUrl = "/".join(urlList[:-1])
            return tmpUrl + '/' + url

#元祖转换为字典
def TupToDict(tup):
    dicts={}
    for t in tup:
        dicts[t[0]]=t[1]
    return dicts

# 检查是否包含关键字
# ^符号表示不包括后面的关键字
def VerifyTitleKey(titleText,title_key):
    if title_key:
        for key in title_key:
            logging.info("关键字：%s", key)
            if key in titleText:
                return True
            elif '^' in key:
                iskey = key.split('^')[0]
                noKey = key.split('^')[1]
                if iskey in titleText and noKey not in titleText:
                    return True
        return False
    else:
        return True

# 判断某路径是否是图片
def GetImgType(imgPath):
    if '.png' in imgPath:
        return 'image/png'
    elif ('.jpg' in imgPath) or ('.jpe' in imgPath) or ('jfif' in imgPath):
        return 'image/jpeg'
    elif '.gif' in imgPath:
        return 'image/gif'
    elif '.bmp' in imgPath:
        return 'image/bmp'
    elif '.tif' in imgPath:
        return 'image/tiff'
    else:
        return False

# 发送邮件到自己的邮箱
def SentEmailWarning(emailTitle, emailContent):
    # 第三方SMTP服务
    mail_host = "smtp.163.com"
    mail_user = "caicai1724"
    mail_pass = "python3test"

    sender = 'caicai1724@163.com'
    receivers = ['caicai1724@163.com']

    msg = MIMEText(emailContent, 'plain', 'utf-8')
    msg['Subject'] = Header(emailTitle, 'utf-8')
    msg['From'] = Header("爬虫脚本错误警告")
    msg['To'] = Header("蔡雁")

    s = smtplib.SMTP()
    s.connect(mail_host, 25)
    s.login(mail_user, mail_pass)
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()

# 身份认证请求
def GetSoupAuth(url, userName, passwd, timeout=10, trynum=5):
    t = 0
    session = requests.session()
    session.auth = (userName, passwd)
    while t < trynum:
        try:
            res = session.get(url, timeout=timeout)
            #res = requests.get(url, auth=HTTPBasicAuth(userName, passwd), timeout=timeout)
            break
        except requests.exceptions.ConnectionError:
            print("ConnectionError")
            t = t + 1
            time.sleep(5)
        except requests.exceptions.ChunkedEncodingError:
            print("ChunkedEncodingError")
            t = t + 1
            time.sleep(5)
        except:
            print("Unfortunitely -- An Unknow Error Happened")
            t = t + 1
            time.sleep(5)
    res.raise_for_status()  # 如果返回不是200，则抛出异常
    if res.encoding == 'ISO-8859-1':
        # encode方法：将字符串转化为你所想要的编码格式，比如utf-8等
        tmp = res.text.encode(res.encoding)
        print(res.apparent_encoding)
        # decode方法：以指定的编码格式解码字符串
        # apparent_encoding：从内容中分析出的响应内容编码方式
        if res.apparent_encoding == 'Windows-1254':
            r = tmp.decode('utf-8')
        else:
            r = tmp.decode(res.apparent_encoding, errors='ignore')
    else:
        r = res.text
    noStarchSoup = bs4.BeautifulSoup(r, 'html.parser')
    return noStarchSoup
