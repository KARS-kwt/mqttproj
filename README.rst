===============
MQTT Communication & Security Module (Under Development)
===============

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: LICENSE

Overview
========
A repurposed version of the `MQTT-PWN project <https://github.com/akamai-threat-research/mqtt-pwn>` 
that demonstrates vulnerabilities and the corresponding security practices of MQTT
communication. Designed to be tailored for the KARS summer lab.



Installation
============

1. Clone the repository:

    .. code-block:: bash

        git clone https://github.com/KARS-kwt/mqttproj

2. Install the dependencies:

    .. code-block:: bash

        pip install -r requirements.txt

Usage
=====


Local Testing
=====
To test the project locally (non-dockerized) set the `MQTT_PWN_TESTING_ENV`
environment variable to `True`:

.. code-block:: bash

    export MQTT_PWN_TESTING_ENV=True

Then run the project:

.. code-block:: bash

    python run.py

To revert to dockerized testing, unset the `MQTT_PWN_TESTING_ENV` environment
variable:

.. code-block:: bash

    unset MQTT_PWN_TESTING_ENV



