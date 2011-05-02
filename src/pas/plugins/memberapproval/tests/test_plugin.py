import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from pas.plugins.memberapproval.tests.layer import MEMBERAPPROVAL_INTEGRATION_TESTING
from pas.plugins.memberapproval.install import manage_add_memberapproval_plugin
from pas.plugins.memberapproval.utils import enablePluginInterfaces, getPAS
from pas.plugins.memberapproval.plugin import APPROVAL_PROPERTY_NAME
from plone.app.testing import TEST_USER_ROLES

USER_ID = 'user_1'
USER_NAME = 'user'
USER_PASSWORD = 'secret'

class PluginUnitTest(unittest.TestCase):

    def testOne(self):
        self.assertEqual(1,1)

class PluginTest(unittest.TestCase):
    
    layer = MEMBERAPPROVAL_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        manage_add_memberapproval_plugin(self.portal.acl_users, "source_users_approval")
        enablePluginInterfaces()
        self.plugin = self.portal.acl_users.source_users_approval
        self.plugin.addUser(
                USER_ID,
                USER_NAME,
                USER_PASSWORD)
        for role in TEST_USER_ROLES:
            self.portal.acl_users.portal_role_manager.doAssignRoleToPrincipal(USER_ID, role)
        
    def _add_property(self, user_id):
        mdata = getToolByName(self.portal, 'portal_memberdata')
        mdata.manage_addProperty(APPROVAL_PROPERTY_NAME, False, 'boolean')

    def testInstalled(self):
        pas = getPAS()
        self.failUnless('source_users' in pas.objectIds())

    def testNoProperty(self):
        self.assertRaises(KeyError, self.plugin.approveUser, USER_ID)

    def testLogin(self):
        self._add_property(USER_ID)
        self.plugin.unapproveUser(USER_ID)
        r = self.plugin.authenticateCredentials(dict(
            login=USER_ID,
            password = USER_PASSWORD
        ))
        self.failIf(r is not None)
        
    def testApproved(self):
        self._add_property(USER_ID)
        self.plugin.approveUser(USER_ID)
        r = self.plugin.authenticateCredentials(dict(
            login=USER_ID,
            password = USER_PASSWORD
        ))
        self.failIf(r is None)

    def testEnumerate(self):
        self._add_property(USER_ID)

        self.assertEqual(len(self.plugin.enumerateUsers()), 1)

        # No approval query - return all
        self.plugin.unapproveUser(USER_ID)
        self.assertEqual(len(self.plugin.enumerateUsers()), 1)

        # Only approved
        r = self.plugin.enumerateUsers(**{APPROVAL_PROPERTY_NAME: True})
        self.assertEqual(len(r), 0)
        
        self.plugin.approveUser(USER_ID)
        r = self.plugin.enumerateUsers(**{APPROVAL_PROPERTY_NAME: True})
        self.assertEqual(len(r), 1)

        r = self.plugin.enumerateUsers(**{APPROVAL_PROPERTY_NAME: False})
        self.assertEqual(len(r), 0)
        
        self.plugin.unapproveUser(USER_ID)
        r = self.plugin.enumerateUsers(**{APPROVAL_PROPERTY_NAME: False})
        self.assertEqual(len(r), 1)
        