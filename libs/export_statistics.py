#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from script.imports import Bugdb
from settings import conf
import datetime
import time
reload(sys)
sys.setdefaultencoding('utf-8')

class ExportStc:

    def __init__(self):
        self.imp = Bugdb(
            'localhost', conf.MYSQLUSERNAME,
            conf.MYSQLPASSWORD, 'hades')

    #获取选择的时间前最靠近的一个
    def get_recent_date(self, errdate):
        self.imp.cur.execute(
                'select MAX(date) from project_static where date < "%s"'
                % errdate)
        recent_date = self.imp.cur.fetchall()
        value = recent_date[0][0]
        return value


    def get_project_static(self, project_name):
        project_static = []
        type_list = ['open', 'fixed', 'regression']
        for item in type_list:
            date_record = []
            one_record = {'data': date_record, 'name': item, 'type': 'line'}
            self.imp.cur.execute(
                'select date,%s from project_static where project_name="%s"'
                % (item, project_name))
            item_info = self.imp.cur.fetchall()
            for info in item_info:
                a = str(info[0])
                b = str(info[1])
                c = [a, b]
                date_record.append(c)
            project_static.append(one_record)
        return project_static

    def get_team_name(self):
        teamid_team = {}
        self.imp.cur.execute('select team,team_id from team')
        team_info = self.imp.cur.fetchall()
        for team in team_info:
            teamid_team[str(team[1])] = str(team[0])
        return teamid_team

    def get_team_static(self, date, project_name):

        yesterday_date = datetime.datetime(
            int(date.split('-')[0]),
            int(date.split('-')[1]),
            int(date.split('-')[2])) \
            + datetime.timedelta(days=-1)
        yesterday_date = str(yesterday_date.year) \
            + '-' \
            + str(yesterday_date.month) \
            + '-' \
            + str(yesterday_date.day)

        big_team_list = [
            'CD_app', 'CD_sys', 'CD_mid',
            'CD_Telecom', 'CD_SPM', 'CD_INT', 'Onsite', 'OTHERS']

        if project_name == 'SAM':
            big_team_list = [
                'CD_app','CD_sys','CD_mid',
                'CD_Telecom','CD_SPM','CD_INT',
                'JRD_zk','OTHERS'
            ]

        team_static = {}
        teamid_team = self.get_team_name()

        for item in big_team_list:
            self.imp.cur.execute(
                'select P0_open,P0_fixed,P0_regression,\
                 P1_open,P1_fixed,P1_regression \
                 from team_static where team_id= \
                 (select team_id from team where team="%s")\
                 and date="%s" and project_name="%s"'
                % (item, date, project_name))
            team_static_p0 = []
            team_static_p1 = []
            little_team_static_p0 = []
            little_team_static_p1 = []
            priority = {'P0': team_static_p0, 'P1': team_static_p1}

            if item not in team_static.keys():
                team_static[item] = priority
            item_info = self.imp.cur.fetchall()
            type_stic_p0 = {'open': 0, 'fixed': 0, 'reg': 0}
            type_stci_p1 = {'open': 0, 'fixed': 0, 'reg': 0}

            for info in item_info:
                type_stic_p0['open'] = int(info[0])
                type_stic_p0['fixed'] = int(info[1])
                type_stic_p0['reg'] = int(info[2])
                type_stci_p1['open'] = int(info[3])
                type_stci_p1['fixed'] = int(info[4])
                type_stci_p1['reg'] = int(info[5])

            self.imp.cur.execute(
                'select P0_fixed,P1_fixed,P0_regression,\
                 P1_regression from team_static \
                 where team_id=(select team_id from team where team="%s")\
                 and date in ("%s","%s")\
                 and project_name="%s"'
                % (item, yesterday_date, date, project_name))
            fixed_info = self.imp.cur.fetchall()
            type_stic_p0['fixed'] = abs(
                int(fixed_info[0][0])-int(fixed_info[1][0]))
            type_stci_p1['fixed'] = abs(
                int(fixed_info[0][1])-int(fixed_info[1][1]))
            type_stic_p0['reg'] = abs(
                int(fixed_info[0][2])-int(fixed_info[1][2]))
            type_stci_p1['reg'] = abs(
                int(fixed_info[0][3])-int(fixed_info[1][3]))

            team_static_p0.append(type_stic_p0)
            team_static_p1.append(type_stci_p1)

            item_member = ()
            if item == 'CD_app':
                item_member = ('APP_leader', 'CD_app1', 'CD_app2', 'CD_app3')
            elif item == 'CD_sys':
                item_member = (
                    'SYS_leader', 'SYS_driver1',
                    'SYS_driver2', 'SYS_sys')
            elif item == 'CD_mid':
                item_member = (
                    'MID_leader', 'MD_connect',
                    'MD_mm', 'MD_frm')
            elif item == 'CD_Telecom':
                item_member = ('CD_Telecom')
            elif item == 'CD_SPM':
                item_member = ('CD_SPM')
            elif item == 'CD_INT':
                item_member = ('CD_INT')
            elif item == 'Onsite':
                item_member = ('Onsite')
            elif item == 'JRD_zk':
                item_member = ('JRD_zk')
            elif item == 'OTHERS':
                item_member = ('OTHERS')

            type_list_p0 = ['P0_open', 'P0_fixed', 'P0_regression']
            type_list_p1 = ['P1_open', 'P1_fixed', 'P1_regression']

            little_team_data_one_p0 = {}
            little_team_data_one_p1 = {}
            little_team_data_p0 = {
                'data': little_team_data_one_p0,
                'name': type_list_p0[0]
                }
            little_team_data_p1 = {
                'data': little_team_data_one_p1,
                'name': type_list_p1[0]
                }
            if item in ['CD_app', 'CD_sys', 'CD_mid']:
                self.imp.cur.execute(
                    'select team_id,%s,%s from team_static \
                     where team_id in(select team_id from team \
                     where team in %s) and date="%s" and project_name="%s"'
                    % (
                        type_list_p0[0], type_list_p1[0],
                        item_member, date, project_name)
                    )
            else:
                self.imp.cur.execute(
                    'select team_id,%s,%s from team_static\
                     where team_id in(select team_id from team where team = "%s")\
                     and date="%s" and project_name="%s"'
                    % (
                        type_list_p0[0], type_list_p1[0],
                        item_member, date, project_name)
                    )
            type_info = self.imp.cur.fetchall()
            for i in type_info:
                little_team_data_one_p0[teamid_team[str(i[0])]] = int(i[1])
                little_team_data_one_p1[teamid_team[str(i[0])]] = int(i[2])

            little_team_static_p0.append(little_team_data_p0)
            little_team_static_p1.append(little_team_data_p1)

            for t in range(1, 3):
                little_team_data_one_p0 = {}
                little_team_data_one_p1 = {}
                little_team_data_p0 = {
                    'data': little_team_data_one_p0,
                    'name': type_list_p0[t]
                    }
                little_team_data_p1 = {
                    'data': little_team_data_one_p1,
                    'name': type_list_p1[t]
                    }
                if item in ['CD_app', 'CD_sys', 'CD_mid']:
                    self.imp.cur.execute(
                        'select team_id,%s,%s from team_static\
                         where team_id in(select team_id from team where team in %s)\
                         and date="%s" and project_name="%s"'
                        % (
                            type_list_p0[t], type_list_p1[t],
                            item_member, yesterday_date,
                            project_name)
                        )
                    type_info = self.imp.cur.fetchall()

                    day_before = {}
                    day_after = {}

                    for row in range(4):
                        if str(type_info[row][0]) not in day_before.keys():
                            day_before[str(type_info[row][0])] = {}
                        day_before[str(type_info[row][0])]['p0'] = int(type_info[row][1])
                        day_before[str(type_info[row][0])]['p1'] = int(type_info[row][2])

                    self.imp.cur.execute(
                        'select team_id,%s,%s from team_static\
                         where team_id in(select team_id from team where team in %s)\
                         and date="%s" and project_name="%s"'
                        % (
                            type_list_p0[t], type_list_p1[t],
                            item_member, date,
                            project_name)
                        )
                    type_info = self.imp.cur.fetchall()

                    for row in range(4):
                        if str(type_info[row][0]) not in day_after.keys():
                            day_after[str(type_info[row][0])] = {}
                        day_after[str(type_info[row][0])]['p0'] = int(type_info[row][1])
                        day_after[str(type_info[row][0])]['p1'] = int(type_info[row][2])

                    for key in day_before.keys():
                        little_team_data_one_p0[teamid_team[key]] = abs(int(day_before[key]['p0'])-int(day_after[key]['p0']))
                        little_team_data_one_p1[teamid_team[key]] = abs(int(day_before[key]['p1'])-int(day_after[key]['p1']))

                    little_team_static_p0.append(little_team_data_p0)
                    little_team_static_p1.append(little_team_data_p1)
                else:
                    self.imp.cur.execute(
                        'select team_id,%s,%s from team_static\
                         where team_id in(select team_id from team where team = "%s")\
                         and date in ("%s","%s") and project_name="%s"'
                        % (
                            type_list_p0[t], type_list_p1[t],
                            item_member, yesterday_date,
                            date, project_name)
                        )
                    type_info = self.imp.cur.fetchall()
                    little_team_data_one_p0[teamid_team[str(type_info[0][0])]] = abs(int(type_info[0][1])-int(type_info[1][1]))
                    little_team_data_one_p1[teamid_team[str(type_info[0][0])]] = abs(int(type_info[0][2])-int(type_info[1][2]))
                    little_team_static_p0.append(little_team_data_p0)
                    little_team_static_p1.append(little_team_data_p1)
            team_static_p0.append(little_team_static_p0)
            team_static_p1.append(little_team_static_p1)
        return team_static

    def get_big_team_static(self, date, project_name):
        yesterday_date = datetime.datetime(
            int(date.split('-')[0]),
            int(date.split('-')[1]),
            int(date.split('-')[2])) \
            + datetime.timedelta(days=-1)
        yesterday_date = str(yesterday_date.year) + '-' \
            + str(yesterday_date.month)\
            + '-' + str(yesterday_date.day)

        # teamid_team = self.get_team_name()
        big_team_static = {}
        big_team_list = [
            'CD_app', 'CD_sys', 'CD_mid',
            'CD_Telecom', 'CD_SPM', 'CD_INT', 'Onsite', 'OTHERS']
        if project_name == 'SAM':
            big_team_list = ['CD_app', 'CD_sys', 'CD_mid',
                            'CD_Telecom', 'CD_SPM', 'CD_INT',
                             'JRD_zk', 'OTHERS']
        # type_list = ['open', 'fixed', 'regression']
        for team in big_team_list:
            self.imp.cur.execute(
                'select P0_open, P1_open from team_static \
                 where team_id in (select team_id from team \
                 where team="%s") and date="%s" and project_name="%s"'
                % (team, date, project_name))
            type_info = self.imp.cur.fetchall()
            a = 0
            for info in type_info:
                a = int(info[0])+int(info[1])
            if team not in big_team_static.keys():
                big_team_static[team] = []
            big_team_static[team].append(str(a))

            self.imp.cur.execute(
                'select P0_fixed,P0_regression,P1_fixed,\
                 P1_regression from team_static\
                 where team_id in (select team_id from team where team="%s")\
                 and date in ("%s","%s") and project_name="%s"'
                % (team, yesterday_date, date, project_name))
            type_info = self.imp.cur.fetchall()
            big_team_static[team].append(
                str(abs(int(type_info[0][0]) -
                    int(type_info[1][0])) +
                    abs(int(type_info[0][2]) -
                    int(type_info[1][2]))))
            big_team_static[team].append(
                str(abs(int(type_info[0][1]) -
                    int(type_info[1][1])) +
                    abs(int(type_info[0][3]) -
                        int(type_info[1][3]))))
        return big_team_static

    def get_bug_list(self, project_name):
        self.imp.cur.execute(
            'select base.bug_id,base.branch,\
             bugusers.email,base.priority,base.bug_status,\
             base.comment_from_cea,base.type,base.regression,base.val_refuse,\
             base.deadline,base.summary from base,bugusers \
             where project_name="%s" and base.assigner=bugusers.id'
            % project_name)
        bug_list = []
        bug_list = self.imp.cur.fetchall()
        return bug_list

    def get_project_total(self, project_list):
        total_project = {}
        for project in project_list:
            alm_project = project
            if project not in total_project.keys():
                total_project[project] = {}
            one_project_total = {'Total Num': 0, 'Task Num': 0, 'Defect Num': 0}
            self.imp.cur.execute(
                'select count(*) from base where project_name="%s"'
                % alm_project)
            result_row = self.imp.cur.fetchall()
            total_count = result_row[0][0]
            one_project_total['Total Num'] = int(total_count)

            self.imp.cur.execute(
                'select count(*) from base where project_name="%s" and type="Defect"'
                #'where project_name="%s" and type="Defect"'
                % alm_project)
            result_row = self.imp.cur.fetchall()
            defect_count = result_row[0][0]
            one_project_total['Defect Num'] = int(defect_count)

            task_count = int(total_count)-int(defect_count)
            one_project_total['Task Num'] = task_count

            total_project[project] = one_project_total
        return total_project

    def get_project_status(self, project_list):
        today = datetime.date.today()
        project_status = {}
        status = ['progress-bar-striped', 'progress-bar-warning',
                'progress-bar-info', 'progress-bar-danger', 'progress-bar-success']
        i = 0
        for project in project_list:
            alm_project = project
            if project not in project_status.keys():
                project_status[project] = []
            self.imp.cur.execute(
                'select dr0,dr1,dr2,dr3,fsr,dr4 from project_status where project_name="%s"'
                #'where project_name="%s"'
                % alm_project)
            result_row = self.imp.cur.fetchall()
            start_time = result_row[0][0]
            end_time = result_row[0][5]

            start_date = str(start_time).split('-')
            end_date = str(end_time).split('-')
            today_date = str(today).split('-')

            total_days = (
                datetime.datetime(
                    int(end_date[0]),
                    int(end_date[1]),
                    int(end_date[2])) -
                datetime.datetime(
                    int(start_date[0]),
                    int(start_date[1]),
                    int(start_date[2]))).days
            now_days = (datetime.datetime(
                int(today_date[0]),
                int(today_date[1]),
                int(today_date[2])) -
                datetime.datetime(
                    int(start_date[0]),
                    int(start_date[1]),
                    int(start_date[2]))).days

            if now_days > total_days:
                project_status[project].append('100')
            else:
                project_status[project].append(str(now_days*100/total_days))
            project_status[project].append(status[i])
            field = []
            for field_desc in self.imp.cur.description:
                field.append(field_desc[0])
            for row in result_row:
                for r in range(5):
                    dr_date = datetime.datetime(
                        int(str(row[r]).split('-')[0]),
                        int(str(row[r]).split('-')[1]),
                        int(str(row[r]).split('-')[2])
                        )
                    if time.mktime(dr_date.timetuple()) > time.time():
                        project_status[project].append(field[r])
                        break
            if len(project_status[project]) == 2:
                project_status[project].append(field[5])

            i += 1
            if i == 5:
                i = 0
        return project_status

    def date_record_yes_no(self, date, project):
        yesterday_date = datetime.datetime(
                int(date.split('-')[0]),
                int(date.split('-')[1]),
                int(date.split('-')[2])) + datetime.timedelta(days=-1)
        yesterday_date = str(yesterday_date.year) + \
            '-' + str(yesterday_date.month) + \
            '-' + str(yesterday_date.day)

        self.imp.cur.execute(
            'select * from project_static \
             where date="%s" and project_name="%s"'
            % (date, project))
        result_date = self.imp.cur.fetchall()

        self.imp.cur.execute(
            'select * from project_static \
             where date="%s" and project_name="%s"'
            % (yesterday_date, project))
        result_yesterday_date = self.imp.cur.fetchall()

        if result_date and result_yesterday_date:
            return True
        else:
            return False

    def get_person_static(self, date, project_name):
        yesterday_date = datetime.datetime(int(date.split('-')[0]), \
            int(date.split('-')[1]),int(date.split('-')[2]))+datetime.timedelta(days=-1)
        yesterday_date = yesterday_date.strftime("%Y-%m-%d")

        big_team_list = [
            'CD_app', 'CD_sys', 'CD_mid',
            'CD_Telecom', 'CD_SPM', 'CD_INT', 'Onsite']
        if project_name == 'SAM':
            big_team_list = [
                'CD_app','CD_sys','CD_mid',
                'CD_Telecom','CD_SPM','CD_INT','JRD_zk']
        #get yesterday data
        person_dict_yesterday = {}
        for team in big_team_list:
            if team not in person_dict_yesterday.keys():
                person_dict_yesterday[team] = {}
        self.imp.cur.execute(
            'select person_static.section, bugusers.email,\
             person_static.P0_fixed, person_static.P1_fixed,\
             person_static.P0_regression, person_static.P1_regression \
             from person_static,bugusers where date="%s" and project_name="%s" \
             and bugusers.id=person_static.user_id'
            % (yesterday_date, project_name))
        result_yesterday_data = self.imp.cur.fetchall()
        for row in result_yesterday_data:
            if person_dict_yesterday.has_key(row[0]):
                if row[1] not in person_dict_yesterday[row[0]].keys():
                    person_dict_yesterday[row[0]][row[1]] = {}
                person_dict_yesterday[row[0]][row[1]] = {'P0_fixed':str(row[2]), 'P1_fixed':str(row[3]),
                                                 'P0_regression':str(row[4]), 'P1_regression':str(row[5])}
        #get today data
        person_dict_today = {}
        for team in big_team_list:
            if team not in person_dict_today.keys():
                person_dict_today[team] = {}
        self.imp.cur.execute(
            'select person_static.section, bugusers.email, person_static.P0_open,\
             person_static.P1_open, person_static.P0_fixed, person_static.P1_fixed,\
             person_static.P0_regression, person_static.P1_regression \
             from person_static,bugusers where date="%s" and project_name="%s" \
             and bugusers.id=person_static.user_id'
            % (date, project_name))
        result_today_data = self.imp.cur.fetchall()
        for row in result_today_data:
            if person_dict_today.has_key(row[0]):
                if row[1] not in person_dict_today[row[0]].keys():
                    person_dict_today[row[0]][row[1]] = {}
                person_dict_today[row[0]][row[1]] = {'P0_open':str(row[2]), 'P1_open':str(row[3]), 'P0_fixed':str(row[4]),
                                        'P1_fixed':str(row[5]), 'P0_regression':str(row[6]), 'P1_regression':str(row[7])}
        #get person_dict_today-person_dict_yesterday
        person_dict = {}
        for team in big_team_list:
            if team not in person_dict.keys():
                person_dict[team] = {}
        for section in person_dict_yesterday.keys():
            for buguser in person_dict_yesterday[section].keys():
                if buguser not in person_dict[section].keys():
                    person_dict[section][buguser] = {}
                person_dict[section][buguser]['P0_open'] = int(person_dict_today[section][buguser]['P0_open'])
                person_dict[section][buguser]['P1_open'] = int(person_dict_today[section][buguser]['P1_open'])
                person_dict[section][buguser]['P0_fixed'] = abs(int(person_dict_today[section][buguser]['P0_fixed'])-int(person_dict_yesterday[section][buguser]['P0_fixed']))
                person_dict[section][buguser]['P1_fixed'] = abs(int(person_dict_today[section][buguser]['P1_fixed'])-int(person_dict_yesterday[section][buguser]['P1_fixed']))
                person_dict[section][buguser]['P0_regression'] = abs(int(person_dict_today[section][buguser]['P0_regression'])-int(person_dict_yesterday[section][buguser]['P0_regression']))
                person_dict[section][buguser]['P1_regression'] = abs(int(person_dict_today[section][buguser]['P1_regression'])-int(person_dict_yesterday[section][buguser]['P1_regression']))
        return person_dict

    def get_functon_id(self):

        """Get a dictionary about function's name and function's id"""

        function_functionid = {}
        self.imp.cur.execute('select function_name,function_id from function')
        function_info = self.imp.cur.fetchall()
        for function in function_info:
            function_functionid[function[0]] = str(function[1])
        return function_functionid

    def get_functions(self, fun_name_id, function_all, sta):

        """Get a dictionary about function'name and bug's number'"""

        functions = {}
        length = len(function_all)
        for i in xrange(0, length):
            one_function = function_all[i]
            for key in fun_name_id.keys():
                if one_function['function_id'] == fun_name_id[key]:
                    functions[key] = int(one_function[sta])
        return functions

    def function_sort(self, fun): 

        """Get a dictionary of top-ten functions on the basis of bug's number"""

        ten_function = {}       
        function_sorted = sorted(fun.items(), key=lambda d:d[1], reverse = True)
        for i in xrange(0, 10):
            ten_function[function_sorted[i][0]] = function_sorted[i][1]
        return ten_function

    def get_function_data(self, date, project_name):

        """Get function's data from function_static table"""

        sql = 'select * from function_static where date="%s" and \
               project_name="%s"' % (date, project_name)
        self.imp.query(sql)
        function_data = self.imp.fetchall()
        return function_data

    def get_one_module(self, ten_function, status, color):

        """Get a dictionary about bug's number, status, color of top-ten functions"""

        one_module = {}
        one_module['data'] = ten_function  
        one_module['name'] = status 
        one_module['color'] = color
        return one_module

    def ten_fun_module(self, date, project_name):

        """Get a list obtain three states of bug and three colors of top-ten functions"""

        yesterday_date = datetime.datetime(int(date.split('-')[0]), \
            int(date.split('-')[1]),int(date.split('-')[2]))+datetime.timedelta(days=-1)
        yesterday_date = yesterday_date.strftime("%Y-%m-%d")

        function_data_1 = self.get_function_data(date, project_name)
        function_data_2 = self.get_function_data(yesterday_date, project_name)

        module = []
        status_list = ['open', 'fixed', 'regression']
        color_list = ['#F6BD0F', '#AFD8F8', '#8BBA00']

        top_ten_fun = {}
        for i in xrange(0, 3):
            fun_1 = self.get_functions(self.get_functon_id(), function_data_1, status_list[i])
            if i is 0:
                top_ten_fun = self.function_sort(fun_1)  
                module.append(self.get_one_module(top_ten_fun, status_list[i], color_list[i]))        
            else:
                fun_2 = self.get_functions(self.get_functon_id(), function_data_2, status_list[i])
                fun = {}
                for key in fun_1.keys():
                    if key in top_ten_fun.keys():
                        if fun_2.has_key(key):
                            fun[key] = fun_1[key] - fun_2[key]
                        else:
                            fun[key] = fun_1[key]
                module.append(self.get_one_module(fun, status_list[i], color_list[i]))
        #self.imp.close()
        return module

"""
test = ExportStc()
print test.get_bug_list("SAM")

test.get_project_static('SAM')
test.get_big_team_static('2016-04-19','SAM')
test.get_team_static('2016-04-20','SAM')
test.ten_fun_module('2016-04-19','SAM')
test.get_person_static('2016-04-20','SAM')
print test.get_person_static('2016-04-19','SAM')
print test.get_big_team_static('2016-03-15','SAM')
print test.ten_fun_module('2016-04-19','SAM')
print test.get_project_static('SAM')
"""
