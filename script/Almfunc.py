#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Connect to ALM and get bug infomation from it"""

import sys
sys.path.append("..")
from settings import conf
import send_mail
from Integrity import IntegrityClient
reload(sys)
sys.setdefaultencoding('utf-8')

class Almfunc:

    """Get bug infomation from ALM"""

    def __init__(self, project):
        self.project = project
        self.typelist = ['Defect', 'Task','Stability Defect']

    def mail_error(self, error):

        """Send mail if Connect fail"""

        conf.MAILCONTENT = conf.MAILCONTENT.join(str(error))
        send_mail.send_mail(conf.MAILUSERNAME, conf.MAILSENDMAIL,
                            conf.MAILSUBJECT, conf.MAILCONTENT,
                            conf.MAILTOLIST, conf.MAILSENDER,
                            conf.MAILPASSWORD)

    def get_alm_connection(self):

        """Connect to ALM"""

        try:
            intclient = IntegrityClient(
              wsdl="http://172.24.147.72:7001/webservices/10/2/Integrity/?wsdl",
              credential_username=conf.ALMUSERNAME,
              credential_password=conf.ALMPASSWORD,
              proxy=dict(http='172.26.35.84:808', https='172.26.35.84:808'))

            return intclient
        except Exception, error:
            print 'not connect'
            sys.exit(1)

    def fetch_bug_id(self, alm_conn, product_name):

        """Get bug's id from ALM"""

        bug_obj = []
        defect_fields = ['ID', 'Type', 'State', 'Summary', 'Assigned User',
                         'SW Release', 'Deadline', 'IPR Value', 'Regression',
                         'Homo', 'Resolution', 'Priority', 'Time To Set New',
                         'Time To Set Assigned', 'Time To Set Verified_SW',
                         'Time To Set Verified', 'Homo', 'Val Refused Date',
                         'VAL Refuse', 'Closed Date', 'Component', 'Function',
                         'Reported By', 'Modified Date', 'Milestone',
                         'Verified_SW Date', 'Comment From CEA',
                         'Created Date', 'LongTextReadOnly']

        for type in self.typelist:
            info_obj = alm_conn.getItemsByFieldValues(fields=defect_fields,
                                            Project=product_name, Type=type)
            if info_obj:
                bug_obj = bug_obj + info_obj
            else:
                list_ = ["<strong>, ", product_name, " ", type, " is 0</strong>"]
                self.mail_error(''.join(list_))
        return bug_obj

    def get_version(self, alm_conn, bug_obj):

        """Get bug's version"""

        item_ids = []
        version_dict = {}
        for bug in bug_obj:
            if bug.type == 'Defect':
                item_ids.append(str(bug.sw_release.IBPL[0]))

        #Remove duplicate elements
        item_id = list(set(item_ids))
        versions = alm_conn.getItemsByIDs(item_ids=item_id,
                                          fields=['ID', 'Project', 'Version'])
        for version in versions:
            version_dict[version.id] = version.Version.shorttext.value
        return version_dict

    def get_branch(self, alm_conn, bug_obj):

        """Get bug's branch"""

        item_ids = []
        branch_dict = {}
        for bug in bug_obj:
            if bug.has_key('singleBranch'):
                item_ids.append(bug.singleBranch.IBPL[0])
        item_id = list(set(item_ids))
        branchs = alm_conn.getItemsByIDs(item_ids=item_id,
                                        fields=['ID', 'Summary'])
        for item in branchs:
            branch_dict[item.id] = item.Summary.shorttext.value
        return branch_dict

    def get_bugs_info(self, info, version, branch):

        """Get all bug's information from ALM"""

        bugs_info = {}
        if not self.project:
            sys.exit(1)

        pro = self.project
        if pro not in bugs_info.keys():
            bugs_info[pro] = {}
        for result in info:
            if result.id not in bugs_info[pro].keys():
                bugs_info[pro][result.id] = {}
            for query in conf.ALMQUERY.keys():
                if query in ('reporter', 'assigned_user'):
                    if result.reporter is None or result.assigned_user is None:
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = 'other@tcl.com'
                    else:
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = str(getattr(result, query).email)
                elif query in ('sw_release'):
                    if result.type == 'Defect':
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = version[result.sw_release.IBPL[0]]
                    else:
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = ''
                elif query in ('Homo'):
                    if result.type == 'Defect':
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = str(result.Homo.shorttext.value)
                    else:
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = ''
                elif query in ('branch'):
                    if result.has_key('singleBranch'):
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = branch[result.singleBranch.IBPL[0]]
                    else:
                        bugs_info[pro][result.id][conf.ALMQUERY[query]] = 'None'
                else:
                    bugs_info[pro][result.id][conf.ALMQUERY[query]] = str(getattr(result, query))

        return bugs_info


#test = Almfunc("/TCT/QCT MSM8976/Idol4 S VF")
#aaa = test.get_alm_connection()
#info = test.fetch_bug_id(aaa, "/TCT/QCT MSM8976/Idol4 S VF")
#version = test.get_version(conn, info)
#branch = test.get_branch(conn, info)
#bug_dict = test.get_bugs_info(info, version, branch)
#print bug_dict
#print info
#for a in info:
    #print a.branch
#version = test.get_version(aaa, info)
#all = test.get_bugs_info(info, version)
#print all
