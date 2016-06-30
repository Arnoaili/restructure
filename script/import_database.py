#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Import data from ALM to database hades"""

from Almfunc import Almfunc
from imports import Bugdb
import sys
sys.path.append("..")
from settings import conf
import os
import logging
import logging.config
import datetime
from bug_statistics import Bugstatistics
from libs.store_redis import StoreRedis
reload(sys)
sys.setdefaultencoding('utf-8')


#logging for fetch info from ALM & write to mysql
logging.config.fileConfig('../settings/log.conf')
logger = logging.getLogger('importLogger')

def main():

    """Import data to database hades"""

    test = Bugdb('localhost', conf.MYSQLUSERNAME, conf.MYSQLPASSWORD, 'hades')
    nowhour = int(datetime.datetime.now().strftime("%H%M"))
    if nowhour in range(900, 1830) and not os.path.exists('./pid/'):
        logger.warning('The dir pid is not exsit, now create it!')
        os.mkdir('./pid/')
        for project in conf.PROJECT_DICT.keys():
            pidfile = './pid/%s' % project
            pid = open(pidfile, 'w+')
            pid.close()
    elif nowhour >1830 and not os.path.exists('./pid/'):
        logger.info("Now all projects info have fetched alreay, exit the script!")
        sys.exit()

    logger.warning("The dir is exsit means there still stay some projects's info can't fetch, now continue...")
    projects_list = os.listdir('./pid/')
    print projects_list
    for project in projects_list:
        loginfo = 'now fetch project %s infomation!' % project
        logger.info('*' * 100)
        logger.info(loginfo)
        alm = Almfunc(conf.PROJECT_DICT[project])
        conn = alm.get_alm_connection()
        try:
            info = alm.fetch_bug_id(conn, conf.PROJECT_DICT[project])
            version = alm.get_version(conn, info)
            branch = alm.get_branch(conn, info)
        except:
            logger.error("Can't connect to ALM!")
            alm.mail_error('<strong>, alm info is null.</strong>')
            sys.exit()

        test.cur.execute("select bug_id from base where project_name='%s'" % (project))
        all_data = test.cur.fetchall()
        yesterday_total_data = 0
        for a in all_data:
            yesterday_total_data += 1
        today_total_data = 0
        for a in info:
            today_total_data += 1 
        logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~yesterday total data : ")
        logger.info(yesterday_total_data)
        logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~today total data : ")
        logger.info(today_total_data)
        if today_total_data < yesterday_total_data-10:
            sys.exit()
        
        logger.info("All info have fetched, now delete the pid file!!")
        rpidfile = './pid/%s' % project
        os.remove(rpidfile)

        logger.info("Now read the value every bug from bug obj!")
        buginfos = alm.get_bugs_info(info, version, branch)

        for key in buginfos.keys():
            for bugkey in buginfos[key].keys():
                test.cur.callproc('import_buginfo',
                    (buginfos[key][bugkey]['closed_date'], 
                     buginfos[key][bugkey]['bug_id'], 
                     buginfos[key][bugkey]['comment_from_cea'], 
                     buginfos[key][bugkey]['type'], 
                     buginfos[key][bugkey]['assigner'],
                     buginfos[key][bugkey]['bug_status'], 
                     buginfos[key][bugkey]['changeddate'], 
                     buginfos[key][bugkey]['summary'], 
                     buginfos[key][bugkey]['ipr_value'], 
                     buginfos[key][bugkey]['deadline'], 
                     buginfos[key][bugkey]['branch'], 
                     buginfos[key][bugkey]['created_date'],
                     buginfos[key][bugkey]['verified_sw_date'], 
                     buginfos[key][bugkey]['reporter_email'],
                     buginfos[key][bugkey]['function_id'],
                     buginfos[key][bugkey]['resolution'], 
                     buginfos[key][bugkey]['regression'], 
                     buginfos[key][bugkey]['val_refuse'], 
                     buginfos[key][bugkey]['priority'],
                     buginfos[key][bugkey]['version'], 
                     buginfos[key][bugkey]['homologation'],
                     buginfos[key][bugkey]['refused_date'],
                     buginfos[key][bugkey]['regression_date'],
                     buginfos[key][bugkey]['new_date'],
                     project))

        sta = Bugstatistics(info)
        logger.info("Now insert all value to MySQL!")
        logger.info("Now insert %s's statistics data to MySQL!" % project)
        sta.statistics(project, logger)
        sta.person_statistics(project, logger)
        logger.info("*" * 100)
    #stroe reids
    sredis = StoreRedis()
    logger.info("Now store today's statistics to redis!")
    #sredis.flush_redis()
    sredis.set_redis(logger)
    sredis.delete_expire(logger)

    if not os.listdir('./pid/'):
        logger.warning("All projects info have fetched, now delete the pid dir!")
        os.removedirs('./pid/')

    test.close()

if __name__ == '__main__':
    main()