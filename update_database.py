# -*- coding: utf-8 -*-

#author：wadelai
#date：2021421
'''
功能: 1.查询华为运维页面的数据
     2.写入对应的数据库
'''
import os
import socket
import csv
import requests
import re
import json
import hashlib
import MySQLdb
import urllib
import urllib3
import ssl
#urllib3.disable_warnings()
from http.client import HTTPSConnection
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ssl._create_default_https_context = ssl._create_unverified_context

def md_screen():
    hash = hashlib.md5()
    hash.update(bytes(password,encoding='utf-8'))
    md_password = hash.hexdigest()
    return md_password

def url_token():
    url = 'https://10.230.9.37:26335/rest/plat/smapp/v1/oauth/token'
    data = {
            "grantType": "password",
            "userName": "cmptest",
            "value": "Y@cmp123"
    }
    header = {
             'Content-Type': 'application/json',
             'Accept': '*/*'
    }
    req = requests.put(url, verify=False, json=data, headers=header)


    if req.status_code == 200:
        response_json = json.loads(req.text)
        if type(response_json) == dict:
            token = response_json.get('accessSession')
        else:
            token = ""
        return token
    else:
        print(req.status_code)
        exit(1)


class Api:

    def __init__(self, token):
        self.headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'X-Auth-Token': token
        }
    def easyrequest(self, uri, method, data):
        url = uri
        if data:
            params = data
        else:
            params = {}
        if method == 'GET':
            response = requests.get(url, verify=False, headers=self.headers)
        if method == 'POST':
            response = requests.post(url, data=params, headers=self.headers)
        if response.status_code == 200:
            try:
                response_json = json.loads(response.text)
                if response_json['code'] == 0:
                    return response_json['data']
                else:
                    print(response.text)
            except Exception as e:
                return response_json
        else:
            print(response.status_code)
            raise Exception("easyrequest %s return %s %s" % (response.url, response.status_code, response.text))

    def get_instance(self, uri, method):
        response = self.easyrequest(uri=uri, method=method, data={})
        print(len(response['content']))
        return response
    # 获取总的cpu、memory、stage
    def get_all(self):
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/resource-pools/25216A596C493169B7D106ECB32E83F8/resource-types/cpu,memory,storage-pool/current-capacities'
        response = self.easyrequest(uri=uri, method='GET', data={})
        memory_ratio = int(response['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'])
        memory_type1 = int(float(response['memory']['oversubscriptionCapacity']['allocatedCapacity']['capacityValue']))
        memory_type2 = int(float(response['memory']['oversubscriptionCapacity']['totalCapacity']['capacityValue']))
        cpu_ratio = int(response['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'])
        cpu_type1 = int(float(response['cpu']['oversubscriptionCapacity']['allocatedCapacity']['capacityValue']))
        cpu_type2 = int(float(response['cpu']['oversubscriptionCapacity']['totalCapacity']['capacityValue']))
        stoge_ratio = int(float(response['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['capacityValue']))
        stoge_type2 = 1823
        stoge_ratio2 = int(stoge_ratio/stoge_type2*100)
        cpu_use = int(response['cpu']['actualCapacity']['usedCapacity']['ratio'])
        memory_use = int(response['memory']['actualCapacity']['usedCapacity']['ratio'])
        stoge_use = int(response['storagePool']['actualCapacity']['usedCapacity']['ratio'])
        # 灾备区裸金属
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/azones/1B4A9EB5CD183134B9E06D9501F791E4/resource-types/cpu,memory,storage-pool/current-capacities'
        uat_bms = self.easyrequest(uri=uri, method='GET', data={})
        uat_bms_cpu = format(uat_bms['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        uat_bms_memory = format(uat_bms['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        uat_bms_stoge = format(uat_bms['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        # 生产区裸金属
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/azones/B3BC268C699C3C409B755507FB1DB486/resource-types/cpu,memory,storage-pool/current-capacities'
        pro_bms = self.easyrequest(uri=uri, method='GET', data={})
        pro_bms_cpu = format(pro_bms['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        pro_bms_memory = format(pro_bms['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        pro_bms_stoge = format(pro_bms['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        # 灾备区虚拟机
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/azones/41C0A08C84B4394D81D59B8E60CBD678/resource-types/cpu,memory,storage-pool/current-capacities'
        uat_ecs = self.easyrequest(uri=uri, method='GET', data={})
        uat_ecs_cpu = format(uat_ecs['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        uat_ecs_memory = format(uat_ecs['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        uat_ecs_stoge = format(uat_ecs['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        # 生产区虚拟机
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/azones/811370A5736C39E1A2155BB3296136DC/resource-types/cpu,memory,storage-pool/current-capacities'
        pro_ecs = self.easyrequest(uri=uri, method='GET', data={})
        pro_ecs_cpu = format(pro_ecs['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        pro_ecs_memory = format(pro_ecs['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        pro_ecs_stoge = format(pro_ecs['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        # 互联网区
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/azones/DB923D022DA03DE8B7C0C6B5EB4D04D4/resource-types/cpu,memory,storage-pool/current-capacities'
        inter = self.easyrequest(uri=uri, method='GET', data={})
        inter_cpu = format(inter['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        inter_memory = format(inter['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        inter_stoge = format(inter['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        # 测试区
        uri = 'https://10.230.9.37:26335/rest/capacity/v1/capbase/azones/139E610D41E738DBBD31ED6F3D382096/resource-types/cpu,memory,storage-pool/current-capacities'
        test = self.easyrequest(uri=uri, method='GET', data={})
        test_cpu = format(test['cpu']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        test_memory = format(test['memory']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')
        test_stoge = format(test['storagePool']['oversubscriptionCapacity']['allocatedCapacity']['ratio'], '.1f')

        conn = MySQLdb.Connect(host='172.19.133.13',
                               port=3306,
                               user='cloudchef',
                               passwd='c10udch3f',
                               db='DataVAutoSrc',
                               charset='utf8')
        cur=conn.cursor()
        cur.execute(
            "update resource_ratio set value = {0},used = {1}, total = {2} where name = 'cpu_ra'".format(cpu_ratio, cpu_type1, cpu_type2))
        cur.execute(
            "update resource_ratio set value = {0} where name = 'cpu_use'".format(cpu_use))
        cur.execute(
            "update resource_ratio set value = {0},used = {1}, total = {2} where name = 'memory_ra'".format(memory_ratio, memory_type1, memory_type2))
        cur.execute(
            "update resource_ratio set value = {0} where name = 'memory_use'".format(memory_use))
        cur.execute(
            "update resource_ratio set value = {0}, used = {1}, total = {2} where name = 'storage_ra'".format(stoge_ratio2, stoge_ratio, stoge_type2))
        cur.execute(
            "update resource_ratio set value = {0} where name = 'storage_use'".format(stoge_use))

        cur.execute(
            "update 6az set hulianwangqu = {0} where name = '互联网区' and id = 1".format(inter_cpu))
        cur.execute(
            "update 6az set hulianwangqu = {0} where name = '互联网区'and id = 2".format(inter_memory))
        cur.execute(
            "update 6az set hulianwangqu = {0} where name = '互联网区' and id = 3".format(inter_stoge))

        cur.execute(
            "update 6az set ceshiqu = {0} where name = '测试区' and id = 1".format(test_cpu))
        cur.execute(
            "update 6az set ceshiqu = {0} where name = '测试区' and id = 2".format(test_memory))
        cur.execute(
            "update 6az set ceshiqu = {0} where name = '测试区' and id = 3".format(test_stoge))

        cur.execute(
            "update 6az set shengluo = {0} where name = '生产区裸金属' and id = 1".format(pro_bms_cpu))
        cur.execute(
            "update 6az set shengluo = {0} where name = '生产区裸金属' and id = 2".format(pro_bms_memory))
        cur.execute(
            "update 6az set shengluo = {0} where name = '生产区裸金属' and id = 3".format(pro_bms_stoge))

        cur.execute(
            "update 6az set zailuo = {0} where name = '灾备区裸金属' and id = 1".format(uat_bms_cpu))
        cur.execute(
            "update 6az set zailuo = {0} where name = '灾备区裸金属' and id = 2".format(uat_bms_memory))
        cur.execute(
            "update 6az set zailuo = {0} where name = '灾备区裸金属' and id = 3".format(uat_bms_stoge))

        cur.execute(
            "update 6az set shengvm = {0} where name = '生产区虚拟机' and id = 1".format(pro_ecs_cpu))
        cur.execute(
            "update 6az set shengvm = {0} where name = '生产区虚拟机' and id = 2".format(pro_ecs_memory))
        cur.execute(
            "update 6az set shengvm = {0} where name = '生产区虚拟机' and id = 3".format(pro_ecs_stoge))

        cur.execute(
            "update 6az set zaivm = {0} where name = '灾备区虚拟机' and id = 1".format(uat_ecs_cpu))
        cur.execute(
            "update 6az set zaivm = {0} where name = '灾备区虚拟机' and id = 2".format(uat_ecs_memory))
        cur.execute(
            "update 6az set zaivm = {0} where name = '灾备区虚拟机' and id = 3".format(uat_ecs_stoge))
        conn.commit()
        conn.close()








if __name__ == '__main__':
    # 获取token
    token = url_token()
    print(token)
    api = Api(token)
    # 获取总的cpu、memory、stage
    api.get_all()

