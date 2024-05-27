# MQTT Communication & Security Module (Under Development)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview
This project is composed of two parts. The first is a set of MQTT clients with a simulator designed
specifically for simulating the environment of the KARS Summer 2024 physical CTF competition. The second part is a repurposed version of the `MQTT-PWN project <https://github.com/akamai-threat-research/mqtt-pwn>` 
that demonstrates vulnerabilities and the corresponding security practices of MQTT
communication. 

## Installation
The following installation and configuration instructions are for a Linux-based
system. The project has been tested on WSL (Ubuntu kernel) and Raspberry Pi OS.

1. Clone the repository:

    ```bash
    git clone https://github.com/KARS-kwt/mqttproj
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

(Under Development)

## Usage

(Under Development)

## Local Testing
To test the project locally (non-dockerized) set the `MQTT_PWN_TESTING_ENV`
environment variable to `True`:

```bash
export MQTT_PWN_TESTING_ENV=True
```

Then run the project:

```bash
python run.py
```

To revert to dockerized testing, unset the `MQTT_PWN_TESTING_ENV` environment
variable:

```bash
unset MQTT_PWN_TESTING_ENV
```


