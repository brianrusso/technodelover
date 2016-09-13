#!/usr/bin/env python

import os

from flask.ext.script import Manager, Server
from flask.ext.script.commands import ShowUrls, Clean
from graphview import run_flask


if __name__ == "__main__":
    run_flask()
