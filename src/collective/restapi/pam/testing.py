# -*- coding: utf-8 -*-
from OFS.Folder import Folder
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2
from plone.uuid.interfaces import IUUIDGenerator
from Testing import ZopeTestCase as ztc
from zope.component import getGlobalSiteManager
from zope.interface import implements

import collective.restapi.pam
import transaction


class CollectiveRestapiPamLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.contenttypes
        import plone.multilingual
        import plone.app.multilingual
        import plone.multilingualbehavior
        import archetypes.multilingual
        import plone.restapi

        self.loadZCML(package=plone.app.contenttypes)
        self.loadZCML(package=plone.multilingual)
        self.loadZCML(package=plone.app.multilingual)
        self.loadZCML(package=archetypes.multilingual)
        self.loadZCML(package=plone.multilingualbehavior)
        self.loadZCML(package=plone.restapi)

        self.loadZCML(package=collective.restapi.pam)

        z2.installProduct(app, "Products.DateRecurringIndex")
        z2.installProduct(app, "plone.app.dexterity")
        z2.installProduct(app, "plone.app.contenttypes")
        z2.installProduct(app, "plone.multilingual")
        z2.installProduct(app, "plone.app.multilingual")
        z2.installProduct(app, "archetypes.multilingual")
        z2.installProduct(app, "plone.multilingualbehavior")
        z2.installProduct(app, "plone.restapi")

        # Support sessionstorage in tests
        app.REQUEST["SESSION"] = self.Session()
        if not hasattr(app, "temp_folder"):
            tf = Folder("temp_folder")
            app._setObject("temp_folder", tf)
            transaction.commit()

        ztc.utils.setupCoreSessions(app)

    def setUpPloneSite(self, portal):

        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )

        login(portal, SITE_OWNER_NAME)

        if portal.portal_setup.profileExists("plone.multilingual:default"):
            applyProfile(portal, "plone.multilingual:default")
        if portal.portal_setup.profileExists("archetypes.multilingual:default"):  # noqa
            applyProfile(portal, "archetypes.multilingual:default")
        if portal.portal_setup.profileExists(
            "plone.multilingualbehavior:default"
        ):  # noqa
            applyProfile(portal, "plone.multilingualbehavior:default")

        applyProfile(portal, "plone.app.dexterity:default")
        applyProfile(portal, "plone.app.contenttypes:default")
        applyProfile(portal, "plone.app.multilingual:default")
        applyProfile(portal, "plone.restapi:default")

        portal.portal_languages.addSupportedLanguage("en")
        portal.portal_languages.addSupportedLanguage("es")
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")


COLLECTIVE_RESTAPI_PAM_FIXTURE = CollectiveRestapiPamLayer()


COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_RESTAPI_PAM_FIXTURE,),
    name="CollectiveRestapiPamLayer:IntegrationTesting",
)


COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_RESTAPI_PAM_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectiveRestapiPamLayer:FunctionalTesting",
)
