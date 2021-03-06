##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
import requests
import config
import helper
import unittest
import json

class GroupTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(GroupTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
       
    def testGet(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain')    
            req = self.endpoint + "/"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            rootUUID = rspJson["root"]
            self.assertTrue(helper.validateId(rootUUID))
        
            req = self.endpoint + "/groups/" + rootUUID
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.failUnlessEqual(rspJson["linkCount"], 2)
            self.failUnlessEqual(rspJson["attributeCount"], 2)
            self.failUnlessEqual(rsp.status_code, 200)
        
    def testGetGroups(self):
        domain = 'tall.' + config.get('domain')    
        headers = {'host': domain}
        req = self.endpoint + "/groups/" 
        rsp = requests.get(req, headers=headers)
        # to do - implement groups (iterate through all groups)
        # self.failUnlessEqual(rsp.status_code, 200)
        # rspJson = json.loads(rsp.text)
          
    def testPost(self):
        # test PUT_root
        domain = 'testGroupPost.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)   
        req = self.endpoint + "/groups"
        headers = {'host': domain}
        # create a new group
        rsp = requests.post(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) 
        rspJson = json.loads(rsp.text)
        self.failUnlessEqual(rspJson["linkCount"], 0)
        self.failUnlessEqual(rspJson["attributeCount"], 0)
        self.assertTrue(helper.validateId(rspJson["id"]) ) 
       
    def testBadPost(self):
        domain = 'tall.' + config.get('domain')    
        req = self.endpoint + "/groups/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.post(req, headers=headers)
        # post is not allowed to provide uri, so should fail
        self.failUnlessEqual(rsp.status_code, 405) 
        
    def testDelete(self):
        domain = 'tall_g2_deleted.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        helper.validateId(rootUUID)
        g2UUID = helper.getUUID(domain, rootUUID, 'g2')
        self.assertTrue(helper.validateId(g2UUID))
        req = self.endpoint + "/groups/" + g2UUID
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("hrefs" in rspJson)
        # do a GET, should return 410 (GONE)
        req = self.endpoint + "/groups/" + g2UUID
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
        
    def testDeleteAnonymous(self):
        # Test deleting anonymous (not linked) group
        domain = 'testGroupDelete.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)   
        req = self.endpoint + "/groups"
        headers = {'host': domain}
        # create a new group
        rsp = requests.post(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) 
        rspJson = json.loads(rsp.text)
        uuid = rspJson["id"]
        self.assertTrue(helper.validateId(uuid))   
        
        req = self.endpoint + "/groups/" + uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # do a GET, should return 410 (GONE)
        req = self.endpoint + "/groups/" + uuid
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
            
        
    def testDeleteBadUUID(self):
        domain = 'tall_g2_deleted.' + config.get('domain')    
        req = self.endpoint + "/groups/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testDeleteRoot(self):
        domain = 'tall.' + config.get('domain')    
        headers = {'host': domain}
        req = self.endpoint + "/"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        rootUUID = rspJson["root"]
        req = self.endpoint + "/groups/" + rootUUID
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 403)
        
    def testGetCollection(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain')    
            req = self.endpoint + "/groups"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            groupIds = rspJson["groups"]
            
            self.failUnlessEqual(len(groupIds), 5)
            for uuid in groupIds:
                self.assertTrue(helper.validateId(uuid))
                
    def testGetCollectionBatch(self):
        domain = 'group1k.' + config.get('domain')   
        req = self.endpoint + "/groups" 
        headers = {'host': domain}
        params = {'Limit': 50 }
        uuids = set()
        # get ids in 20 batches of 50 links each
        last_uuid = None
        for batchno in range(20):
            if last_uuid:
                params['Marker'] = last_uuid
            rsp = requests.get(req, headers=headers, params=params)
            self.failUnlessEqual(rsp.status_code, 200)
            if rsp.status_code != 200:
                break
            rspJson = json.loads(rsp.text)
            groupIds = rspJson['groups']
            self.failUnlessEqual(len(groupIds) <= 50, True)
            for groupId in groupIds:
                uuids.add(groupId)
                last_uuid = groupId
            if len(groupIds) == 0:
                break
        self.failUnlessEqual(len(uuids), 1000)  # should get 1000 unique uuid's    
    
       
if __name__ == '__main__':
    unittest.main()