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

class ShapeTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ShapeTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))    
       
    def testGet(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        g2_uuid = helper.getUUID(domain, root_uuid, 'g2')
        dset21_uuid = helper.getUUID(domain, g2_uuid, 'dset2.1') 
        req = helper.getEndpoint() + "/datasets/" + dset21_uuid + "/shape"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['class'], 'H5S_SIMPLE')
        self.assertEqual(len(rspJson['dims']), 1)
        self.assertEqual(rspJson['dims'][0], 10)  
        self.assertEqual(rspJson['maxdims'][0], 10)
        
    def testGetResizable(self):
        domain = 'resizable.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        resizable_1d_uuid = helper.getUUID(domain, root_uuid, 'resizable_1d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_1d_uuid + "/shape"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 1)
        self.assertEqual(rspJson['dims'][0], 10)  
        self.assertEqual(rspJson['maxdims'][0], 20)
        
        resizable_2d_uuid = helper.getUUID(domain, root_uuid, 'resizable_2d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_2d_uuid + "/shape"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 2)
        self.assertEqual(rspJson['dims'][1], 10)  
        self.assertEqual(rspJson['maxdims'][1], 20)
        
        unlimited_1d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_1d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_1d_uuid + "/shape"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 1)
        self.assertEqual(rspJson['dims'][0], 10)  
        self.assertEqual(rspJson['maxdims'][0], 0)
        
        unlimited_2d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_2d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_2d_uuid + "/shape"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 2)
        self.assertEqual(rspJson['dims'][1], 10)  
        self.assertEqual(rspJson['maxdims'][1], 0)
        
    def testGetFill(self):
        domain = 'fillvalue.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/shape"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['class'], 'H5S_SIMPLE')
        self.assertEqual(len(rspJson['dims']), 2)
        self.assertEqual(rspJson['dims'][0], 10)  
        self.assertEqual(rspJson['maxdims'][1], 10)
        self.assertEqual(rspJson['fillvalue'], 42)
        
       
    def testPutResizable(self):
        domain = 'resized.' + config.get('domain')
        headers = {'host': domain}
        root_uuid = helper.getRootUUID(domain)
        resizable_1d_uuid = helper.getUUID(domain, root_uuid, 'resizable_1d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_1d_uuid + "/shape"
        payload = { 'shape': 20 }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 1)
        self.assertEqual(rspJson['dims'][0], 20)  
        self.assertEqual(rspJson['maxdims'][0], 20)       
         
        resizable_2d_uuid = helper.getUUID(domain, root_uuid, 'resizable_2d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_2d_uuid + "/shape"
        payload = { 'shape': [10, 20] }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 2)
        self.assertEqual(rspJson['dims'][0], 10)
        self.assertEqual(rspJson['dims'][1], 20)  
        self.assertEqual(rspJson['maxdims'][0], 10)
        self.assertEqual(rspJson['maxdims'][1], 20)
               
        unlimited_1d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_1d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_1d_uuid + "/shape"
        payload = { 'shape': 25 }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 1)
        self.assertEqual(rspJson['dims'][0], 25)  
        self.assertEqual(rspJson['maxdims'][0], 0)
        
        unlimited_2d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_2d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_2d_uuid + "/shape"
        payload = { 'shape': [10, 25] }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['dims']), 2)
        self.assertEqual(rspJson['dims'][0], 10)  
        self.assertEqual(rspJson['maxdims'][0], 10)
        self.assertEqual(rspJson['dims'][1], 25)  
        self.assertEqual(rspJson['maxdims'][1], 0)   
        
        
        
    def testPutInvalidShape(self):
        domain = 'resized.' + config.get('domain')
        headers = {'host': domain}
        root_uuid = helper.getRootUUID(domain)
        resizable_1d_uuid = helper.getUUID(domain, root_uuid, 'resizable_1d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_1d_uuid + "/shape"
        payload = { 'shape': [20, 10] }  # wrong rank
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
        payload = { 'shape': 8 }  # try to shrink
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)        
                  
        resizable_2d_uuid = helper.getUUID(domain, root_uuid, 'resizable_2d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_2d_uuid + "/shape"
        payload = { 'shape': [12, 20] }  # try to extend non-extendable dimension
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
     
    
        
if __name__ == '__main__':
    unittest.main()