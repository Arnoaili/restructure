#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configure file"""

# MySQL conf
MYSQLUSERNAME = "root"
MYSQLPASSWORD = "admin0"


# connect ALM conf
ALMUSERNAME = "cd.int"
ALMPASSWORD = "Cd123456"

# query bug info from ALM
ALMQUERY = {'id': 'bug_id', 'state': 'bug_status', 
            'modified_date': 'changeddate',
            'deadline': 'deadline', 'summary': 'summary', 
            'ipr_value': 'ipr_value',
            'regression': 'regression', 'created_date':'created_date', 
            'closed_date': 'closed_date','val_refuse': 'val_refuse', 
            'priority': 'priority', 'function': 'function_id',
            'branch': 'branch', 'type': 'type','resolution': 'resolution', 
            'comment_from_cea': 'comment_from_cea',
            'reporter': 'reporter_email', 'assigned_user':'assigner',
            'sw_release':'version', 'homo':'homologation',
            'verified_sw_date':'verified_sw_date',
            'refused_date':'refused_date',
            'regression_date':'regression_date',
            'new_date':'new_date'
            }


# sent mail conf
MAILUSERNAME = "cd.int"
MAILPASSWORD = "Cd123456"
MAILSENDER = "BugWeb"
MAILSUBJECT = "Error from BugWeb"
MAILCONTENT = "<strong>Please check the log from BugWeb</strong>"
MAILTOLIST = ["mei.yang@tcl.com"]
MAILSENDMAIL = "cd.int@tcl.com"

#project_list
PROJECT_DICT = { 'Gandalf':'/TCT/QCT MSM8976/Idol4 S VF',
                    'SAM':'/TCT/MTK MT6580M/PIXI4-4 3G VF',
                    'Frodo':'/TCT/MTK MT6735M/Pixi4-5 4G VF',
                    'Aragorn':'/TCT/MTK MT6755M/SHINE PLUS VF',
		          'Smeagol' : '/TCT/MTK MT6572M/PIXI3-3.5 3G VF'}
