#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for the flicker_bot.

This module performs the start-up, login and reads out the settings to configure
the flicker_bot.
"""


def start():
    from flicker_bot.app import main
    main()

if __name__ == '__main__':
    start()
