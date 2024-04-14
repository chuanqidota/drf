import os

from cryptography.fernet import Fernet


class ConfObj:
    @staticmethod
    def get_conf():
        # get running env
        env = os.getenv('drfEnv', None)

        # default is developer env config
        conf_default = {
            # 通用配置
            'DEBUG': True,
            'SECRET_KEY': '75XiJ5DWL33kcYRxwvyNRLXY3quvqAiNDYesnybo0xM=',
            'ALLOWED_HOSTS': ['*'],

            # 日志配置
            'LOG_LEVEL': 'DEBUG',

            # 数据库配置 配置按自身需求调整 MYSQL_PASS->python
            'MYSQL_NAME': 'drf',
            'MYSQL_HOST': '127.0.0.1',
            'MYSQL_PORT': '3306',
            'MYSQL_USER': 'root',
            'MYSQL_PASSWORD': 'gAAAAABmDzXLs5W4o3VsfiAG6819KpCMP7LBuOWMqhSdCMjSmYC-C7-c'
                              '8XHTBcMv80NJhuTOnmSNqtBmnAYE8imQCF563Hp4pg==',

            # redis
            'REDIS_HOST': '',
            'REDIS_PORT': '',
            'REDIS_PASSWD': '',
            'REDIS_BROKER_DB': '',
            'REDIS_CACHE_DB': '',

            # es配置-配置安自身需求调整
            'ES_HOST_PORT': ['http://127.0.0.1:9200'],
            'ES_USERNAME': '',
            'ES_PASSWORD': '',

            # 网站url
            "WEB_URL": "http://127.0.0.1:8000"

        }

        # test env config
        if env == 'test':
            conf_default.update({
                # 通用配置
                'DEBUG': True,
                'SECRET_KEY': '75MwqpAAIOLS0szN-X79V13n0JyXTsYt854L6D_oGQs=',

                # 日志配置
                'LOG_LEVEL': 'DEBUG',

                # 数据库配置
                'MYSQL_NAME': 'drf',
                'MYSQL_HOST': '',
                'MYSQL_PORT': '',
                'MYSQL_USER': '',
                'MYSQL_PASSWORD': '',

                # redis
                'REDIS_HOST': '',
                'REDIS_PORT': '',
                'REDIS_PASSWD': '',
                'REDIS_BROKER_DB': '',
                'REDIS_CACHE_DB': '',

                # es配置
                'ES_HOST_PORT': [],
                'ES_USERNAME': '',
                'ES_PASSWORD': '',

                # 网站url
                "WEB_URL": "http://127.0.0.1:8000"
            })

        # product env config
        if env == 'prod':
            conf_default.update({
                # 通用配置
                'DEBUG': False,
                'SECRET_KEY': 'msgzsY0O3bYF-TkxrJGf2zAwojT_8pr7lFy8AzvpJW4=',
                'ALLOWED_HOSTS': ['域名'],
                # 数据库配置
                'MYSQL_NAME': 'drf',
                'MYSQL_HOST': '',
                'MYSQL_PORT': '',
                'MYSQL_USER': '',
                'MYSQL_PASSWORD': '',

                # 日志配置
                'LOG_LEVEL': 'INFO',

                # redis
                'REDIS_HOST': '',
                'REDIS_PORT': '',
                'REDIS_PASSWD': '',
                'REDIS_BROKER_DB': '',
                'REDIS_CACHE_DB': '',

                # es配置
                'ES_HOST_PORT': [''],
                'ES_USERNAME': '',
                'ES_PASSWORD': '',

                # 网站url
                "WEB_URL": "http://127.0.0.1:8000"
            })

        return conf_default

    @staticmethod
    def decrypt(s):
        """
            解密
            s: 加密字符串
        """
        if isinstance(s, str):
            s = s.encode()
        assert isinstance(s, bytes)
        f = Fernet(ConfObj.get_conf().get('SECRET_KEY'))
        return f.decrypt(s).decode()
