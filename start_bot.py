#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for the flicker_bot.

This module performs the start-up, login and reads out the settings to configure
the flicker_bot.
"""
if __name__ == '__main__':
    from flicker_bot.run import main as run_bot
    run_bot()
