# -*- coding: utf-8 -*-
from base64 import b64encode
from collective.restapi.pam.testing import (
    COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING,
)  # noqa
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from freezegun import freeze_time
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.testing import applyProfile
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.locking.interfaces import ITTWLockable
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import register_static_uuid_utility
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.statictime import StaticTime
from plone.testing.z2 import Browser
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.site.hooks import getSite

import collections
import json
import os
import pkg_resources
import re
import transaction
import unittest


try:
    # p.a.multilingual < 1.2
    pkg_resources.get_distribution("plone.multilingual")
    from plone.multilingual.interfaces import ITranslationManager
    from plone.multilingual.interfaces import ILanguage

except pkg_resources.DistributionNotFound:
    # p.a.multilingual >1.1, < 2
    from plone.app.multilingual.interfaces import ITranslationManager
    from plone.app.multilingual.interfaces import ILanguage

REQUEST_HEADER_KEYS = ["accept", "authorization", "lock-token"]

RESPONSE_HEADER_KEYS = ["content-type", "allow", "location"]

base_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "docs/source/_json"
)


def pretty_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))


def save_request_and_response_for_docs(name, response):
    with open("{}/{}".format(base_path, "%s.req" % name), "w") as req:
        req.write(
            "{} {} HTTP/1.1\n".format(
                response.request.method, response.request.path_url
            )
        )
        ordered_request_headers = collections.OrderedDict(
            sorted(response.request.headers.items())
        )
        for key, value in ordered_request_headers.items():
            if key.lower() in REQUEST_HEADER_KEYS:
                req.write("{}: {}\n".format(key.title(), value))
        if response.request.body:
            # If request has a body, make sure to set Content-Type header
            if "content-type" not in REQUEST_HEADER_KEYS:
                content_type = response.request.headers["Content-Type"]
                req.write("Content-Type: %s\n" % content_type)

            req.write("\n")

            # Pretty print JSON request body
            if content_type == "application/json":
                json_body = json.loads(response.request.body)
                body = pretty_json(json_body)
                # Make sure Content-Length gets updated, just in case we
                # ever decide to dump that header
                response.request.prepare_body(data=body, files=None)

            req.write(response.request.body)

    with open("{}/{}".format(base_path, "%s.resp" % name), "w") as resp:
        status = response.status_code
        reason = response.reason
        resp.write("HTTP/1.1 {} {}\n".format(status, reason))
        for key, value in response.headers.items():
            if key.lower() in RESPONSE_HEADER_KEYS:
                resp.write("{}: {}\n".format(key.title(), value))
        resp.write("\n")
        resp.write(response.content)


class TestDocumentationBase(unittest.TestCase):
    def setUp(self):
        self.statictime = self.setup_with_context_manager(StaticTime())

        self.app = self.layer["app"]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        # Register custom UUID generator to produce stable UUIDs during tests
        pushGlobalRegistry(getSite())
        register_static_uuid_utility(prefix="SomeUUID")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic %s:%s" % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def setup_with_context_manager(self, cm):
        """Use a contextmanager to setUp a test case.
        Registering the cm's __exit__ as a cleanup hook *guarantees* that it
        will be called after a test run, unlike tearDown().
        This is used to make sure plone.restapi never leaves behind any time
        freezing monkey patches that haven't gotten reverted.
        """
        val = cm.__enter__()
        self.addCleanup(cm.__exit__, None, None, None)
        return val

    def tearDown(self):
        popGlobalRegistry(getSite())
        self.api_session.close()


class TestDocumentation(TestDocumentationBase):

    layer = COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentation, self).setUp()
        # self.app = self.layer["app"]
        # self.request = self.layer["request"]
        # self.portal = self.layer["portal"]
        # self.portal_url = self.portal.absolute_url()

        # # Register custom UUID generator to produce stable UUIDs during tests
        # pushGlobalRegistry(getSite())
        # register_static_uuid_utility(prefix="SomeUUID")

        # self.time_freezer = freeze_time("2016-10-21 19:00:00")
        # self.frozen_time = self.time_freezer.start()

        # self.api_session = RelativeSession(self.portal_url)
        # self.api_session.headers.update({"Accept": "application/json"})
        # self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # setRoles(self.portal, TEST_USER_ID, ["Manager"])

        language_tool = api.portal.get_tool("portal_languages")
        language_tool.addSupportedLanguage("en")
        language_tool.addSupportedLanguage("es")
        # Setup language root folders
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        en_id = self.portal["en"].invokeFactory(
            "Document", id="test-document", title="Test document"
        )
        self.en_content = self.portal["en"].get(en_id)

        es_id = self.portal["es"].invokeFactory(
            "Document", id="test-document", title="Test document"
        )
        self.es_content = self.portal["es"].get(es_id)

        import transaction

        transaction.commit()
        # self.browser = Browser(self.app)
        # self.browser.handleErrors = False
        # self.browser.addHeader(
        #     "Authorization", "Basic %s:%s" % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        # )

    # def tearDown(self):
    #     super(TestDocumentation, self).tearDown()
    #     self.time_freezer.stop()
    #     # popGlobalRegistry(getSite())

    def test_documentation_translations_post(self):
        response = self.api_session.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"id": self.es_content.absolute_url()},
        )
        save_request_and_response_for_docs("translations_post", response)

    def test_documentation_translations_post_by_id(self):
        response = self.api_session.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"id": self.es_content.absolute_url().replace(self.portal_url, "")},
        )
        save_request_and_response_for_docs("translations_post_by_id", response)

    def test_documentation_translations_post_by_uid(self):
        response = self.api_session.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"id": self.es_content.UID()},
        )
        save_request_and_response_for_docs("translations_post_by_uid", response)

    def test_documentation_translations_get(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = self.api_session.get(
            "{}/@translations".format(self.en_content.absolute_url())
        )

        save_request_and_response_for_docs("translations_get", response)

    def test_documentation_translations_delete(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = self.api_session.delete(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"language": "es"},
        )
        save_request_and_response_for_docs("translations_delete", response)

    def test_translations_is_expandable(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = self.api_session.get(self.en_content.absolute_url())

        save_request_and_response_for_docs("translations_is_expandable", response)

    def test_expand_translations(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = self.api_session.get(
            self.en_content.absolute_url() + "?expand=translations"
        )

        save_request_and_response_for_docs("expand_translations", response)
