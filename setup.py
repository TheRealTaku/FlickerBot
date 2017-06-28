from setuptools import setup

setup(
    name='FlickerBot',
    version='0.1dev1',
    description=open('README.md').read(),
    packages=['flicker_admin', 'flicker_utils', 'flicker_bot', 'flicker_bot.plugins', 'flicker_bot.utils'],
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Flask',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='flicker discord bot',
    url='https://github.com/Lissaa/FlickerBot'
)
