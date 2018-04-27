Upgrade guide
=============

This upgrade guide lists all breaking changes in collective.restapi.pam and explains the
necessary steps that are needed to upgrade to the lastest version.

Upgrading to collective.restapi.pam 2.0.0
-----------------------------------------

When using the `@translations` endpoint in collective.restapi.pam 1.x, the endpoint returned a `language` key
with the content object's language and a `translations` key with all its translations.

Now, as the endpoint is expandable we want the endpoint to behave like the other expandable endpoints.
As top level information we only include the name of the endpoint on the `@id` attribute and the actual
translations of the content object in an attribute called `items`.

This means that now the JSON response to a GET request to the :ref:`translations` endpoint does not
include anymore the language of the actual content item and the translations in an attribute called
`items` instead of `translations`.

Old response::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/en/test-document",
    "language": "en",
    "translations": [
      {
        "@id": "http://localhost:55001/plone/es/test-document",
        "language": "es"
      }
    ]
  }

New response::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/en/test-document/@translations",
    "items": [
      {
        "@id": "http://localhost:55001/plone/es/test-document",
        "language": "es"
      }
    ]
  }
