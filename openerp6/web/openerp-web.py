#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Start script for the openerp-web project.

This script is only needed during development for running from the project
directory. When the project is installed, easy_install will create a
proper start script.
"""
import openobject.commands

if __name__ == "__main__":
    openobject.commands.start()
