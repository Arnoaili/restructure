#!/usr/bin/env python
# -*- coding: utf-8 -*-

from imports import Bugdb
import sys
sys.path.append("..")
from settings import conf
import datetime
from bug_statistics import Bugstatistics


dbs = Bugdb('localhost', conf.MYSQLUSERNAME, conf.MYSQLPASSWORD, 'hades')

def insert_function_static(table_name, insert_id, data):
    dbs.cur.execute('replace into %s values(%s, "%s", %s, %s, %s, %s, "%s")'
            % (table_name, insert_id, data['date'], data['total'], data['open'], 
               data['fixed'], data['regression'], data['project']))
    dbs.conn.commit()

def insert_project_static(table_name, data):
    dbs.cur.execute('replace into %s values("%s", "%s", %s, %s, %s, %s, %s)'
            % (table_name, data['project'], data['date'], data['total'], data['open'], 
               data['fixed'], data['regression'], "NULL"))
    dbs.conn.commit()

def insert_team_static(table_name, insert_id, data):
    dbs.cur.execute('replace into %s values(%s, "%s", %s, %s, %s, %s, %s, %s, "%s")'
            % (table_name, insert_id, data['date'], data['P0_open'], data['P0_fixed'], 
               data['P0_regression'], data['P1_open'], data['P1_fixed'], 
               data['P1_regression'], data['project']))
    dbs.conn.commit()

def insert_person_static(table_name, insert_id, data):
    dbs.cur.execute('replace into %s values(%s, %s, "%s", %s, %s, %s, %s, %s, %s, "%s", "%s")'
            % (table_name, "NULL", insert_id, data['section'], data['P0_open'], data['P1_open'],
               data['P0_fixed'], data['P1_fixed'], data['P0_regression'],data['P1_regression'],
               data['project'], data['date']))
    dbs.conn.commit()

def team_id(import_time_1, project):
    dbs.cur.execute('select team_id from team')
    teamid = dbs.cur.fetchall()
    team_dict = {}
    for eachid in teamid:
        team_dict[eachid[0]] = {'P0_open':0, 'P0_fixed':0, 'P0_regression':0,
                                'P1_open':0, 'P1_fixed':0, 'P1_regression':0,
                                'date':import_time_1[:10], 'project':project}
    return team_dict

def get_user_userid(import_time_1, project):
    person_dict = {}
    dbs.cur.execute('select id,section from bugusers where department="swd1"')
    user_info = dbs.cur.fetchall()
    for user in user_info: 
        if user[0] not in person_dict.keys():
            person_dict[user[0]] = {'P0_open':0, 'P1_open':0, 'P0_fixed':0, 'P1_fixed':0,
                                    'P0_regression':0, 'P1_regression':0, 'section':user[1],
                                    'date':import_time_1[:10], 'project':project}
    return person_dict

def get_lost_data(import_time_1, import_time_2, project):
    dbs.cur.execute('select function_id,team_id,priority,assigner from base,bugusers \
        where ((verified_sw_date<"%s" and verified_sw_date!="%s") or (closed_date<"%s" and verified_sw_date="%s")) \
        and bug_status in ("Delivered","Verified_SW","Closed","Verified") \
        and bugusers.id=base.assigner and project_name="%s"' 
        % (import_time_1, import_time_2, import_time_1, import_time_2, project))
    all_data_3 = dbs.cur.fetchall()

    dbs.cur.execute('select function_id,team_id,priority,assigner from base,bugusers \
        where regression="YES" \
        and bugusers.id=base.assigner and project_name="%s"' % (project))
    all_data_4 = dbs.cur.fetchall()    

    ######################################################
    dbs.cur.execute('select function_id,team_id,priority,assigner from base,bugusers \
        where created_date< "%s" and bug_status in ("Delivered","Verified_SW","Closed","Verified","Opened","Assigned","New","Resolved")\
        and bugusers.id=base.assigner and project_name= "%s"' % (import_time_1, project))
    all_data_5 = dbs.cur.fetchall()
    i = 0
    for hh in all_data_5:
        i += 1
    dbs.cur.execute('select function_id,team_id,priority,assigner from base,bugusers \
        where ((verified_sw_date<"%s" and verified_sw_date!="%s") or (closed_date<"%s" and verified_sw_date="%s")) and \
        bugusers.id=base.assigner and bug_status in ("Delivered","Verified_SW","Closed","Verified")\
        and project_name="%s"' % (import_time_1, import_time_2, import_time_1, import_time_2, project))
    all_data_6 = dbs.cur.fetchall()
    j = 0
    for hh in all_data_6:
        j += 1
    print i, j, i-j, project
    ###########################################################

    team_dict = team_id(import_time_1, project)
    function_dict = {}
    person_dict = get_user_userid(import_time_1, project)
    project_dict = {'total':0, 'open':0, 'fixed':0, 'regression':0,
                    'date':import_time_1[:10], 'project':project}

    for all_data in (all_data_5, all_data_3, all_data_4):
        for each_data in all_data:
            if each_data[0] not in function_dict.keys():
                function_dict[each_data[0]] = {'total':0, 'open':0, 'fixed':0, 'regression':0,
                                               'date':import_time_1[:10], 'project':project}
            if all_data == all_data_5:
                function_dict[each_data[0]]['open'] += 1
                project_dict['open'] += 1
                if each_data[2] == 'P0 (Urgent)':
                    team_dict[each_data[1]]['P0_open'] += 1
                    if each_data[3] in person_dict.keys():
                        person_dict[each_data[3]]['P0_open'] += 1
                elif each_data[2] == 'P1 (Quick)':
                    team_dict[each_data[1]]['P1_open'] += 1
                    if each_data[3] in person_dict.keys():
                        person_dict[each_data[3]]['P1_open'] += 1

            elif all_data == all_data_3:
                function_dict[each_data[0]]['fixed'] += 1
                project_dict['fixed'] += 1
                if each_data[2] == 'P0 (Urgent)':
                    team_dict[each_data[1]]['P0_fixed'] += 1
                    if each_data[3] in person_dict.keys():
                        person_dict[each_data[3]]['P0_fixed'] += 1
                elif each_data[2] == 'P1 (Quick)':
                    team_dict[each_data[1]]['P1_fixed'] += 1
                    if each_data[3] in person_dict.keys():
                        person_dict[each_data[3]]['P1_fixed'] += 1
            else:
                function_dict[each_data[0]]['regression'] += 1
                project_dict['regression'] += 1
                if each_data[2] == 'P0 (Urgent)':
                    team_dict[each_data[1]]['P0_regression'] += 1
                    if each_data[3] in person_dict.keys():
                        person_dict[each_data[3]]['P0_regression'] += 1
                elif each_data[2] == 'P1 (Quick)':
                    team_dict[each_data[1]]['P1_regression'] += 1
                    if each_data[3] in person_dict.keys():
                        person_dict[each_data[3]]['P1_regression'] += 1
            if all_data != all_data_4:
                function_dict[each_data[0]]['total'] += 1
                project_dict['total'] += 1

    for each_data in all_data_6:
        function_dict[each_data[0]]['open'] -= 1
        function_dict[each_data[0]]['total'] -= 1
        project_dict['open'] -= 1
        project_dict['total'] -= 1
        if each_data[2] == 'P0 (Urgent)':
            team_dict[each_data[1]]['P0_open'] -= 1
            if each_data[3] in person_dict.keys():
                person_dict[each_data[3]]['P0_open'] -= 1
        elif each_data[2] == 'P1 (Quick)':
            team_dict[each_data[1]]['P1_open'] -= 1
            if each_data[3] in person_dict.keys():
                person_dict[each_data[3]]['P1_open'] -= 1



    for teamid in team_dict.keys():
        if teamid in (19, 30, 31, 33):
            big_teamid = 36
        elif teamid in (20, 21, 22, 35):
            big_teamid = 37
        elif teamid in (24, 25, 26, 34):
            big_teamid = 38
        else:
            continue
        team_dict[big_teamid]['P0_open'] += team_dict[teamid]['P0_open']
        team_dict[big_teamid]['P1_open'] += team_dict[teamid]['P1_open']
        team_dict[big_teamid]['P0_fixed'] += team_dict[teamid]['P0_fixed']
        team_dict[big_teamid]['P1_fixed'] += team_dict[teamid]['P1_fixed']
        team_dict[big_teamid]['P0_regression'] += team_dict[teamid]['P0_regression']
        team_dict[big_teamid]['P1_regression'] += team_dict[teamid]['P1_regression']

    #print person_dict
    #print team_dict
    
    for key in function_dict.keys():
        insert_function_static("function_static", key, function_dict[key])
    insert_project_static("project_static", project_dict)
    for key in team_dict.keys():
        insert_team_static("team_static", key, team_dict[key])
    for key in person_dict.keys():
        insert_person_static("person_static", key, person_dict[key])
    
if __name__ == '__main__':
    import_time_1 = '2016-06-28 00:00:00' # lost date
    import_time_2 = '0000-00-00 00:00:00'
    #p_list = ['Gandalf'] # lost project
    for project in conf.PROJECT_DICT.keys():
    	#for project in p_list:    
        get_lost_data(import_time_1, import_time_2, project)
