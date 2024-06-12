import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'mysql+pymysql://avnadmin:AVNS_hrn0LHM7VvaHN41aI--@mysql-cashyangu-cashyangu.i.aivencloud.com:22606/defaultdb?ssl-mode=REQUIRED'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
