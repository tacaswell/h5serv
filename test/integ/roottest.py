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

class RootTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RootTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
        
    def testGet(self):
        domain = 'tall.' + config.get('domain')   
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        helper.validateId(rspJson["root"])
        
    def testGetReadOnly(self):
        domain = 'tall_ro.' + config.get('domain')    
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        helper.validateId(rspJson["root"])
        
    def testGetNotFound(self):
        domain = 'doesnotexist.' + config.get('domain')    
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testWrongTopLevelDomain(self):
        domain = "www.hdfgroup.org"    
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 403)  # 403 == Forbidden
        
    def testInvalidDomain(self):
        # can't be just a bare top-level domain
        domain = config.get('domain')  
        # get top-level domain. e.g.: 'test.hdf.io' -> 'hdf.io'
        npos = domain.find('.')
        topdomain = domain[npos+1:] 
        req = self.endpoint + "/"
        headers = {'host': topdomain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 403)  # 403 == Forbidden
        
        domain = 'two.dots..are.bad.' + config.get('domain')   
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)  # 400 == bad syntax
        
        domain = 'missingenddot' + topdomain   
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)  # 400 == bad syntax
        
        # just a dot is no good
        domain = '.' + topdomain  
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)  # 400 == bad syntax
        
        domain =  '.dot.in.front.is.bad.' + config.get('domain')   
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)  # 400 == bad syntax
        
    def testDomainWithSpaces(self):
        domain = 'filename with space.' + config.get('domain')    
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        
    def testGetSubdomain(self): 
        domain = 'zerodim.subdir.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        
    def testPutSubdomain(self): 
        domain = 'newfile.newsubdir.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        rspJson = json.loads(rsp.text)
        
    def testPutSubSubdomain(self): 
        domain = 'newfile.newsubsubdir.newsubdirparent.' + config.get('domain')        
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        rspJson = json.loads(rsp.text)
        href = (rspJson["hrefs"][0])[u"href"]
        self.failUnlessEqual(href, 
        u"http://newfile.newsubsubdir.newsubdirparent.test.hdf.io/")
               
    def testDelete(self):
        #test DELETE_root
        domain = 'deleteme.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
    def testDeleteReadonly(self):
        #test DELETE_root
        domain = 'readonly.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 403)
        
    def testDeleteNotFound(self):
        domain = 'doesnotexist.' + config.get('domain')    
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testDeleteSubSubdomain(self): 
        domain = 'deleteme.subdir.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)

    def testPut(self):
        # test PUT_root
        domain = 'newfile.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        rspJson = json.loads(rsp.text)
        
if __name__ == '__main__':
    unittest.main()