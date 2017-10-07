# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.restapi.pam


class CollectiveRestapiPamLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.restapi.pam)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.restapi.pam:default')


COLLECTIVE_RESTAPI_PAM_FIXTURE = CollectiveRestapiPamLayer()


COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_RESTAPI_PAM_FIXTURE,),
    name='CollectiveRestapiPamLayer:IntegrationTesting'
)


COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_RESTAPI_PAM_FIXTURE,),
    name='CollectiveRestapiPamLayer:FunctionalTesting'
)


COLLECTIVE_RESTAPI_PAM_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_RESTAPI_PAM_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveRestapiPamLayer:AcceptanceTesting'
)
