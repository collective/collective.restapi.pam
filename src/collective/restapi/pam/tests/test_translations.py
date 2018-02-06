# -*- coding: utf-8 -*-
from base64 import b64encode
from collective.restapi.pam.testing import COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING  # noqa
from collective.restapi.pam.testing import COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING  # noqa
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from unittest import TestCase
from zope.component import getMultiAdapter
from zope.event import notify
from ZPublisher.pubevents import PubStart

import pkg_resources
import requests
import transaction

try:
    # p.a.multilingual < 1.2
    pkg_resources.get_distribution('plone.multilingual')
    from plone.multilingual.interfaces import ITranslationManager
    from plone.multilingual.interfaces import ILanguage

except pkg_resources.DistributionNotFound:
    # p.a.multilingual >1.1, < 2
    from plone.app.multilingual.interfaces import ITranslationManager
    from plone.app.multilingual.interfaces import ILanguage


class TestTranslationInfo(TestCase):

    layer = COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        # Setup language root folders
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)

    def test_translation_info_includes_translations(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request),
            name=u'GET_application_json_@translations')

        info = tinfo.reply()
        self.assertIn('items', info)
        self.assertEqual(1, len(info['items']))

    def test_correct_translation_information(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request),
            name=u'GET_application_json_@translations')

        info = tinfo.reply()
        tinfo_es = info['items'][0]
        self.assertEqual(
            self.es_content.absolute_url(),
            tinfo_es['@id'])
        self.assertEqual(self.es_content.Language(), tinfo_es['language'])


class TestLinkContents(TestCase):
    layer = COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        # Setup language root folders
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)

        untranslated_en_id = self.portal.en.invokeFactory(
            id='untranslated-test-document',
            type_name='Document',
            title='Test document'
        )
        self.untranslated_en_content = self.portal.en.get(untranslated_en_id)
        untranslated_es_id = self.portal.es.invokeFactory(
            id='untranslated-test-document',
            type_name='Document',
            title='Test document'
        )
        self.untranslated_es_content = self.portal.es.get(untranslated_es_id)

    def traverse(self, path='/plone', accept='application/json',
                 method='POST'):
        request = self.layer['request']
        request.environ['PATH_INFO'] = path
        request.environ['PATH_TRANSLATED'] = path
        request.environ['HTTP_ACCEPT'] = accept
        request.environ['REQUEST_METHOD'] = method
        request._auth = 'Basic %s' % b64encode(
            '%s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        notify(PubStart(request))
        return request.traverse(path)

    def test_translation_link_without_id_gives_400(self):
        service = self.traverse('/plone/en/test-document/@translations')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual(
            'Missing content id to link to', res['error']['message'])

    def test_translation_link_with_invalid_id_gives_400(self):
        self.request['BODY'] = '{"id": "http://server.com/unexisting-id"}'
        service = self.traverse('/plone/en/test-document/@translations')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual(
            'Content does not exist', res['error']['message'])

    def test_translation_link_already_translated(self):
        self.request['BODY'] = '{"id": "http://nohost/plone/es/test-document"}'
        service = self.traverse('/plone/en/test-document/@translations')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual(
            'Already translated into language es', res['error']['message'])

    def test_translation_linking_succeeds(self):
        self.request['BODY'] = '{"id": "http://nohost/plone/es/untranslated-test-document"}' # noqa
        service = self.traverse(
            '/plone/en/untranslated-test-document/@translations')
        service.reply()
        self.assertEqual(201, self.request.response.getStatus())


class TestUnLinkContents(TestCase):
    layer = COLLECTIVE_RESTAPI_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        # Setup language root folders
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)

        untranslated_en_id = self.portal.en.invokeFactory(
            id='untranslated-test-document',
            type_name='Document',
            title='Test document'
        )
        self.untranslated_en_content = self.portal.en.get(untranslated_en_id)
        untranslated_es_id = self.portal.es.invokeFactory(
            id='untranslated-test-document',
            type_name='Document',
            title='Test document'
        )
        self.untranslated_es_content = self.portal.es.get(untranslated_es_id)

    def traverse(self, path='/plone', accept='application/json',
                 method='POST'):
        request = self.layer['request']
        request.environ['PATH_INFO'] = path
        request.environ['PATH_TRANSLATED'] = path
        request.environ['HTTP_ACCEPT'] = accept
        request.environ['REQUEST_METHOD'] = method
        request._auth = 'Basic %s' % b64encode(
            '%s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        notify(PubStart(request))
        return request.traverse(path)


    def test_translation_unlink_invalid_language_returns_400(self):
        self.request['BODY'] = '{"language": "fr"}'
        service = self.traverse(
            '/plone/en/test-document/@translations', method='DELETE')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual(
            'This object is not translated into fr', res['error']['message'])

    def test_translation_unlink_without_language_returns_400(self):
        service = self.traverse(
            '/plone/en/test-document/@translations', method='DELETE')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual(
            'You need to provide the language to unlink',
            res['error']['message']
        )

    def test_translation_unlinking_succeeds(self):
        self.request['BODY'] = '{"language": "es"}'
        service = self.traverse(
            '/plone/en/test-document/@translations', method='DELETE')
        res = service.reply()
        self.assertEqual(204, self.request.response.getStatus())


class TestLinkContentsFunctional(TestCase):
    layer = COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        # Setup language root folders
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        transaction.commit()

    def test_translation_linking_succeeds(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'id': self.es_content.absolute_url(),
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        for language, translation in manager.get_translations():
            if language == ILanguage(self.es_content).get_language():
                self.assertEqual(translation, self.es_content)

    def test_calling_endpoint_without_id_gives_400(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
            },
        )
        self.assertEqual(400, response.status_code)

    def test_calling_endpoint_with_invalid_id_gives_400(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'id': 'http://server.com/this-content-does-not-exist'
            },
        )
        self.assertEqual(400, response.status_code)


class TestUnLinkContentsFunctional(TestCase):
    layer = COLLECTIVE_RESTAPI_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        # Setup language root folders
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)
        transaction.commit()

    def test_translation_unlinking_succeeds(self):
        response = requests.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'language': 'es',
            },
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        for language, translation in manager.get_translations():
            if language == ILanguage(self.es_content).get_language():
                self.assertEqual(translation, self.es_content)

    def test_calling_endpoint_without_language_gives_400(self):
        response = requests.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
            },
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_untranslated_content_gives_400(self):
        ITranslationManager(self.en_content).remove_translation("es")
        transaction.commit()
        response = requests.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'language': 'es',
            },
        )
        self.assertEqual(400, response.status_code)
