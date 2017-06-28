from flicker_admin.app import setup_admin, app
from flicker_utils.sql_app import Base, Currency, Setting
import os

os.environ.setdefault('DATABASE_URL', 'postgres://fxliwryvtdlvvg:5a00ac945d55f66506a9f9'
                                      '4100568589e80ac48cdc71f7fd5a126cc4904a450a@ec2-10'

                                      '7-20-186-238.compute-1.amazonaws.com:5432/d1omuu8v0nq9vh')
os.environ.setdefault('SECRET_KEY', 'MySecretKey')
setup_admin(Base, Currency, Setting)
app.run()
