..
      Copyright 2017 OpenPassPhrase
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

.. _configuration:

Configuration
=============

OpenPassPhrase is configurable via configuration files aggregated from several
sources:

    1. User supplied file: this can be passed into various tools such as
       ``opp-db`` on the command line.
    2. User's home directory: ``~/.opp/opp.cfg``.
    3. System directory: ``/etc/opp/opp.cfg``.

Config files (if exist) from all three sources are cascaded together in such
a manner where duplicate values which occur later are simply ignored.
Thus, highest override priority is afforded to the user supplied config and
lowest to the system config.

The config files contain options for configuring various parts of the service.
The format is similar to standard INI file with options specified one per line
and organized under sections. For example::

    [DEFAULT]
    option1 = value1

    [USER]
    option1 = value2
    option2 = value3

.. note:: You **must** include at least **one** section in your config file,
    otherwise the configuration loading will fail. The **only** section
    currently being read is ``[DEFAULT]``.

The following options are currently configurable for OpenPassPhrase:

``db_connect``

    ============    ======
    **Type:**       string

    **Default:**    None
    ============    ======

    Used by SQLAlchemy to establish a connection to the database.

    **Example:**

    | ``db_connect = mysql://<user>:<password>@<host>/<db>``
    |   or
    | ``db_connect = sqlite:////<full_path_to_db_file>``

``secret_key``

    ============    =================================
    **Type:**       string

    **Default:**    'default-insecure'
    ============    =================================

    Used by the web server to encode and decode the signature component of the
    JSON Web Token (JWT). Refer to :ref:`front-end` description for more
    information about JWT. It is similarly used by the web app UI endpoints to
    secure the user's login session cookie from tampering.

    **Example:**

    | ``secret_key = large random value``

``exp_delta``

    ============    =======
    **Type:**       integer

    **Default:**    300
    ============    =======

    This is the value in **seconds** that determines when the JWT will expire
    starting from issue time. After expiration, the token will not be
    accepted and users will have to login to generate a new token. It is also
    used in a similar manner by the web app UI endpoints to epxire the user's
    login session.

    **Example:**

    | ``exp_delta = 3600``
