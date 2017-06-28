#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for the flicker_bot admin site.

This module performs the start-up, login and reads out the settings to configure
the flicker_bot admin site.
"""


def start():
    from flicker_admin.app import setup_admin, app
    from flicker_utils.sql_app import Base, Currency, Setting
    setup_admin(Base, Currency, Setting)
    app.run(debug=False)

if __name__ == '__main__':
    start()
