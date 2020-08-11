#!/usr/bin/env python3
from gevent import monkey
monkey.patch_all()
import config
from utils.server import MallServer, Application
from api import *


def register_url():
    app = MallServer.app
    app.register_blueprint(user.app, url_prefix='/user')
    app.register_blueprint(es_product_service.app, url_prefix='/esProduct')
    @app.route('/')
    def index():
        return 'yes'


if __name__ == '__main__':
    MallServer.init_register = register_url
    MallServer.config = config.ServerConfig
    Application.main()
