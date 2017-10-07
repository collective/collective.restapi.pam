# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.restapi.pam.testing import COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.restapi.pam is properly installed."""

    layer = COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.restapi.pam is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.restapi.pam'))

    def test_browserlayer(self):
        """Test that ICollectiveRestapiPamLayer is registered."""
        from collective.restapi.pam.interfaces import (
            ICollectiveRestapiPamLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveRestapiPamLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.restapi.pam'])

    def test_product_uninstalled(self):
        """Test if collective.restapi.pam is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.restapi.pam'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveRestapiPamLayer is removed."""
        from collective.restapi.pam.interfaces import \
            ICollectiveRestapiPamLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveRestapiPamLayer, utils.registered_layers())
