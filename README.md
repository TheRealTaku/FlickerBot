# Flicker Bot

A personal discord bot running on discord.py framework, using Heroku and Flask.

 1. Run `pip install -r requirements.txt` to install all the requirement libraries.
 2. Recommended (If you want to publish this app): A free [Heroku](https://www.heroku.com) account. Better to add a credit card to use the free Heroku Postgresql and Iron Cache.
 3. Define the following environment variables:
    * `DISCORD_TOKEN`: The token to your discord bot, register [here](https://discordapp.com/developers/applications/me) if you don't have one yet, and copy the `token` field by first clicking `click to reveal`.
    * `DISCORD_EMAIL` *optional*: The email to your discord account, *if you want to login to your discord account instead (You still need to create a dummy `DISCORD_TOKEN` environment variable)*.
    * `DISCORD_PASSWORD` *optional*: The password to your discord account, *if you want to login to your discord account instead (You still need to create a dummy `DISCORD_TOKEN` environment variable)*.
    * `SERCET_KEY`: A random secret string used to for Flask admin.
 4. Also define the following environment variables if not ran from heroku or Heroku Postgresql and/or Iron Cache add-on isn't enabled:
    * `DATABASE_URL`: The url to the Postgresql or any SQL database, if you don't have any, you type a local file address to create a sqlite database. It's automatically defined if you used Heroku Postgresql.
    * `IRON_CACHE_PROJECT_ID`: *Soon to be optional*, comes with when used Iron Cache as a Heroku add-on.
    * `IRON_CACHE_TOKEN`: *Soon to be optional*, comes with when used Iron Cache as a Heroku add-on.
 5. 