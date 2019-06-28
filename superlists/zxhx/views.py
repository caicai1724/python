from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.exceptions import ValidationError
import logging
import json
from zxhx.models import *
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'publicClass'))
import zsy_interface

logger = logging.getLogger("django")

def home_page(request):
    zxhxPro = ZxhxProduct.objects.all()
    trainFile = TrainFile.objects.all().order_by('sort_id')
    tool = Tool.objects.all()
    CoachLog.objects.create(coach_name='yk', interface_id=1)
    return render(request, 'jszchome.html', {"zxhxPro": zxhxPro, "trainFile": trainFile, "tool": tool})

# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {"error": ''})
    else:
        uname = request.POST['username']
        pswordTemp = request.POST['password']
        pswordobj = Password.objects.filter(plain_wd=pswordTemp)
        if len(pswordobj):
            psword = pswordobj[0].cipher_wd
        else:
            pswordobj = Coach.objects.filter(coach_name=uname)
            if len(pswordobj):
                psword = pswordobj[0].password
            else:
                return render(request, 'login.html', {"error": 'The password is unsupported!'})
        loginList = zsy_interface.zsy_login(uname, psword)
        if 'error' in loginList:
            return render(request, 'login.html', {"error": loginList['error']})
        request.session['sessionId'] = loginList['sessionId']
        request.session['sig'] = loginList['sig']
        request.session['time'] = loginList['time']
        request.session['userName'] = loginList['userName']
        request.session['schoolId'] = loginList['schoolId']
        CoachLog.objects.create(coach_name=loginList['userName'], interface_id=2)
        return redirect(f'/zxhx/examList/page/1')
        # return render(request, 'login.html',{"error":'success!!'})

def examList(request, pagenum):
    examList,cookies = zsy_interface.zsy_print(request.session, pagenum)
    request.session['cookies'] = cookies
    #return render(request, 'examlist.html', {'examList': json.dumps(examList)})
    return render(request, 'examlist.html', {'examList': examList, 'pageNum': str(pagenum)})

def sendLableTask(request):
    result = zsy_interface.zsy_sendlabeltask(request.POST['examId'], request.POST['examName'], request.POST['type'], request.POST['status'], request.session['cookies'])
    examList,cookies = zsy_interface.zsy_print(request.session,'')
    if 'success' in result or '试题标注任务创建成功' in result:
    	errorInfo = '发送标注成功'
    else:
    	errorInfo = result
    CoachLog.objects.create(coach_name=request.session['userName'], interface_id=3)
    return render(request, 'examlist.html', {'examList': examList, 'errorInfo': errorInfo, 'pageNum': '1'})

def base(request):
    return render(request, 'Mybase.html')

def export(request, pagenum):
    examList = zsy_interface.zsy_export(request.session['cookies'], pagenum)
    return render(request, 'export.html', {'examList': examList, 'pageNum': str(pagenum)})
  
def SetReport(request):
    if 'word' in request.POST:
        fileType = 'word'
    else:
        fileType = 'excel'
    return render(request,'setReport.html',{'examId': request.POST['examId'],'fileType': fileType})

def downReport(request):
    datas = {
        'exam_id': request.POST['examId'],
        'file_type': request.POST['fileType'],
        #'score_section_list': ''
    }
    datalist = request.POST.getlist('reportData[]')
    if 'studentCard' in datalist:
        datas['student_card'] = 1
    if 'schoolStudentCard' in datalist:
        datas['school_student_card'] = 1
    if 'isOuter' in datalist:
        datas['is_outer'] = 1
    if 'idNumber' in datalist:
        datas['id_number'] = 1
    CoachLog.objects.create(coach_name=request.session['userName'], interface_id=4)
    
    fileUrl = zsy_interface.zsy_ajaxDown(request.session['cookies'], datas)
    fileName = fileUrl.split('/')[-1]
    return render(request, 'fileDown.html', {'fileUrl': fileUrl, 'fileName': fileName})

def modelExam(request):
    IPstr, dbstr, groupId = zsy_interface.zsy_dbname(str(request.session['schoolId']))
    request.session['IPstr'] = IPstr
    request.session['dbstr'] = dbstr
    request.session['groupId'] = groupId
    examList = zsy_interface.zsy_examList_model(IPstr, dbstr)
    if len(examList) == 0:
        error = '本学期内没有标识为范文的考试！'
    return render(request, 'modelExam.html', {'examList': examList, 'error': error})
    
def modelEssay(request):
    studentList = zsy_interface.zsy_model_essay_by_examGroupId(request.POST['examGroupId'], request.session['IPstr'], request.session['dbstr'], request.session['groupId'])
    return render(request, 'modelStudent.html', {'studentList': studentList})
