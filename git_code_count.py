#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import os
import re
import requests
import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf8')

#get 100 user, project infomation
def get100_info(info,page=1):
    url = 'http://192.168.14.100/api/v4/' + info + '?private_token=BPXeLCg7j31yyxbQ4SL4&per_page=100'+'&page='+str(page)
    str1 = requests.get(url)
    l1 = str1.json()
    l2 = []
    for i in l1:
        if info == "users":
            l2.append(i["username"])
        if info == "projects":
            l2.append(i["ssh_url_to_repo"])
    return l2

#get all projects
def get_all_projects():
    page = 1
    projects = [] 
    while True:
        pros = get100_info("projects",page)
        print pros
        for pro in pros:
            projects.append(pro)
        page += 1
        print page
        if len(pros) < 100:
            break
    print projects
    return projects

#get all users
def get_all_users():
    page = 1
    users = []
    while True:
        us = get100_info("users",page)
        for u in us:
            users.append(u)
        page += 1
        if len(us) < 100:
            break
    print users
    return users

#Clone each item and do the statistics of each item for each person first
def clone_all_project():
    today = datetime.datetime.now()
    offset = datetime.timedelta(days=-1)
    yesterday = (today + offset).strftime('%Y-%m-%d')
    ssh_url_repo = get_all_projects()
    #print(ssh_url_repo)
    os.system('rm -rf /data/gitcount/*')
    count_list = []
    try:
        for ssh_url in ssh_url_repo:
            os.chdir('/data/gitcount')
            print ssh_url
            clone_cmd = "git clone " + ssh_url
            #print(clone_cmd)
            os.system(clone_cmd)
            project_dir = ssh_url.split('/')[1].split('.')[0:-1]
            project_dir = '.'.join(project_dir)
            #print(project_dir)
            os.chdir('/data/gitcount/' + project_dir)
            users_list = get_all_users()
            #print(users_list)
            for user in users_list:
                code_count_cmd = "git log --all --author='" + user + "' --after='" + yesterday + "' --pretty=tformat: --numstat | " \
                                 "gawk \'{ add += $1 ; subs += $2 ; loc += $1 - $2 }; END {printf \"%s*%s*%s\",add,subs,loc}\'"
                #print(code_count_cmd)
                code_count =  os.popen(code_count_cmd).read()
                out = code_count.split('*')
                out.insert(0,user)
                #print out 
                count_list.append(out)
        #print count_list
    except Exception as err:
        print('Error:{}'.format(err))
    return  count_list

#Analyze each person's additions, deletions, and changes to all items
def everyb_crud():
    collect_data = clone_all_project()
    #print  collect_data  
    users_list = get_all_users()
    allperson_list = []
    for user in users_list:
        allperson_list.append([user,0,0,0])  
    #print allperson_list
    for code in  collect_data:
        for user in allperson_list:
            if code[0] == user[0]:
                user[0] = code[0]
                user[1] += int(code[1]) if code[1] != '' else 0
                user[2] += int(code[2]) if code[2] != '' else 0
                user[3] += int(code[3]) if code[3] != '' else 0
    
    total_count = sorted(allperson_list,key=lambda A:int(A[1]),reverse=True)
    #print total_count
    dingding(total_count)
                        
# dingding notify
def dingding(l1):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=1a632df7c2a9d0c029de54f12815c788d3808d6c846d4931a655202898b00271'
    HEADERS = {"Content-Type": "application/json;charset=utf-8"}
    #content = 'Author\t\t\t\t\t\t昨天add\t\t\t\t\t\t昨天delete\t\t\t\t\t\t昨天total\n'
    content = ''
    for i in l1:
        user, add, delete, total = i[0].strip(), str(i[1]), str(i[2]), str(i[3])
        str_uer_add_delete = user + '\t\t\t\t\t\t' + add + '\t\t\t\t\t\t' + delete + '\t\t\t\t\t\t' + total + '\n'
        content += str_uer_add_delete
    with open('/root/gitcount.txt','w+') as f:
        f.seek(0)
        f.truncate()
        f.write(content)
        #os.system("sed -i '1d' /root/gitcount.txt")
    #重新定义倒序后的content
    #new_content = 'Author\t\t\t\t\t\t昨天add\t\t\t\t\t\t昨天delete\t\t\t\t\t\t昨天total\n' + '\n'.join(lll)
    String_textMsg = {"msgtype": "text", "text": {"content": content}}
    #print(String_textMsg)
    String_textMsg = json.dumps(String_textMsg)
    #res = requests.post(url, data=String_textMsg, headers=HEADERS)
    #print(String_textMsg)       

if __name__ == "__main__":
    everyb_crud()
