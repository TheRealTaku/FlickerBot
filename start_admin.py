#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for the flicker_bot admin site.

This module performs the start-up, login and reads out the settings to configure
the flicker_bot admin site.
"""
if __name__ == '__main__':
    from flicker_admin.app import run_admin
    run_admin()
