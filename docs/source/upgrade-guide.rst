Upgrade guide
=============

This upgrade guide lists all breaking changes in collective.restapi.pam and explains the
necessary steps that are needed to upgrade to the lastest version.

Upgrading to collective.restapi.pam 2.0.0
-----------------------------------------

The JSON response to a GET requests to the :ref:`translations` endpoint does not include
anymore the language of the actual content item.

The JSON response to a GET requests to the :ref:`translations` endpoint includes the actual
translations in an attribute called `items` instead of `translations`.

These changes were done to behave like the other existing endpoints that are also expandable, which as
top level information only include the name of the endpoint on the `id` attribute and the actual
information in an attribute called `items`.
