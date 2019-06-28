from django.db import models

# Create your models here.
class Coach(models.Model):
    coach_name = models.CharField(max_length=25)
    coach_id = models.SmallIntegerField(default=0)
    real_name = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    school_id = models.SmallIntegerField(default=0)
    
class ZxhxProduct(models.Model):
    name = models.CharField(max_length=100)
    downUrl = models.CharField(max_length=255,blank=True)
    info = models.CharField(max_length=1000,blank=True)

class fileType(models.Model):
    type_id = models.SmallIntegerField(default=0)
    name = models.CharField(max_length=100)

class TrainFile(models.Model):
    name = models.CharField(max_length=100)
    type_id = models.ForeignKey(to="fileType", db_column="type_id", on_delete=models.PROTECT)
    playUrl = models.CharField(max_length=255,blank=True)
    downUrl = models.CharField(max_length=255,blank=True)
    extracted_code = models.CharField(max_length=25,blank=True)
    info = models.CharField(max_length=1000,blank=True)
    sort_id = models.SmallIntegerField(default=0)

class Tool(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    downUrl = models.CharField(max_length=255,blank=True)
    info = models.CharField(max_length=1000,blank=True)

class CoachLog(models.Model):
    coach_name = models.CharField(max_length=100, default='')
    interface_id = models.SmallIntegerField()
    call_time = models.DateTimeField(auto_now=True)

class Password(models.Model):
    plain_wd = models.CharField(max_length=25)
    cipher_wd = models.CharField(max_length=100)

class Interface(models.Model):
    interface_name = models.CharField(max_length=100)


