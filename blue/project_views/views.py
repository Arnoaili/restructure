#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, request
import sys
#sys.path.append('..')
sys.path.append('../..')
from libs.export_statistics import ExportStc
from libs.store_redis import StoreRedis
import datetime
from settings import conf
import json
from . import project_views

@project_views.route('/',methods=['GET', 'POST'])
def index():
    date = ""
    if request.method == 'POST':
        date = request.form['date']

    if date == "":
		date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")

    project_name = []
    for project in conf.PROJECT_DICT.keys():
        project_name.append(project)

    daily_statistics = ExportStc()
    projects = daily_statistics.get_project_total(project_name)
    total_sort = ('Total Num', 'Task Num', 'Defect Num')

    project_status = daily_statistics.get_project_status(project_name)

    return render_template('index.html', total_sort = total_sort, 
                           projects = projects, project_name = project_name, 
                           project_status = project_status, date = date)

@project_views.route('/flot/<value>',methods = ['GET', 'POST'])
def flot(value):

    date = ""
    if request.method == 'POST':
        date = request.form['date']

    if date == "":
        date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")

    date_list = date.split('/')
    year = date_list[2]
    day = date_list[1]
    month = date_list[0]
    display_date = year+'-'+month+'-'+day

    project_name = []
    for project in conf.PROJECT_DICT.keys():
        project_name.append(project)

    daily_statistics = ExportStc()
    daily_redis = StoreRedis()

    teams_sort = ('CD_app', 'CD_sys', 'CD_mid', 'CD_Telecom', 'CD_SPM', 'CD_INT', 'Onsite', 'OTHERS')
    if conf.PROJECT_DICT[value] == "/TCT/MTK MT6580M/PIXI4-4 3G VF":
        teams_sort = ('CD_app','CD_sys','CD_mid','CD_Telecom','CD_SPM','CD_INT','JRD_zk','OTHERS')

    if daily_statistics.date_record_yes_no(display_date, value):
        print 'enter if record_yes_no'
        if daily_redis.get_redis(display_date, value):
            print 'enter if'
            daily = json.dumps(daily_redis.get_redis(display_date, value)['project_static'])
            module = json.dumps(daily_redis.get_redis(display_date, value)['function_static'])
            teams_total = daily_redis.get_redis(display_date, value)['big_team_static']
            teams = daily_redis.get_redis(display_date, value)['team_static']
            team_detail = daily_redis.get_redis(display_date, value)['person_static']
        
        else:
            print 'enter else'
            daily = daily_statistics.get_project_static(value)
            module = daily_statistics.ten_fun_module(display_date, value)
            teams_total = daily_statistics.get_big_team_static(display_date, value)
            teams = daily_statistics.get_team_static(display_date, value)
            team_detail = daily_statistics.get_person_static(display_date, value)

        return render_template('flot.html', teams_sort = teams_sort,
                               daily = daily, module = module, teams = teams, teams_total=teams_total,
                               project_name = project_name, date = date, team_detail = team_detail)
    else:
        correct_date = daily_statistics.get_recent_date(display_date)
        return render_template('error.html', date=date, coodate = correct_date, project_name = project_name)

@project_views.route('/table/<value>',methods=['GET', 'POST'])
def table(value):

    date = ""
    if request.method == 'POST':
        date = request.form['date']

    if date == "":
		date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")

    project_name = []
    for project in conf.PROJECT_DICT.keys():
        project_name.append(project)
    daily_statistics = ExportStc()
    result = daily_statistics.get_bug_list(value)

    return render_template('tables.html', result = result, 
                            project_name = project_name, date = date)



"""
from flask_restful import Api, Resource
from flask import render_template

class Hello(Resource):
    def get(self):
        return 'hello world! I am here !!!'
		#return render_template('hoo.html')

api = Api(blue)
api.add_resource(Hello, '/')
"""
