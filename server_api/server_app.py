# -*- coding: utf-8 -*-
"""
Серверное приложение для API и g4f UI
"""
from os import getenv

import gevent.pywsgi
import g4f

from flask import request, jsonify
from flask_cors import CORS

from g4f.gui import app
from g4f.gui.server import website, backend

from server_api.schedule import html_daily
from rasp_api.log_conf import *

try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=path.join(path.dirname(path.abspath(__file__)), "../files/.env"))
except ModuleNotFoundError:
    pass

g4f.logging = False

CORS(app)
host, port = getenv("host"), int(getenv("port"))


@app.route('/v1/api/schedule', methods=['POST'])
def daily_schedule():
    """
    :return: jsonified html of daily schedule
    """
    data = request.json
    return jsonify({'message': "".join(html_daily(data["groupname"]))})


@app.route('/v1/api/gpt', methods=['POST'])
def ask_gpt():
    """
    :return: jsonified one way chatgpt response
    """
    prompt = request.json["prompt"]

    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_35_turbo,
        messages=[{"role": "user", "content": prompt}])

    if len(response) > 2900:
        response = "Ошибка. Попробуйте ещё раз."

    return jsonify({"answer": response})


def run_app(local: bool = False):
    """
    запускает Flask-приложение для API и Gpt4Free UI приложения.
    :param bool local: localhost/host
    """
    if local:
        host_ = "localhost"
    else:
        host_ = host

    site = website.Website(app)
    for route in site.routes:
        app.add_url_rule(
            route,
            view_func=site.routes[route]['function'],
            methods=site.routes[route]['methods'],
        )

    backend_api = backend.Backend_Api(app)
    for route in backend_api.routes:
        app.add_url_rule(
            route,
            view_func=backend_api.routes[route]['function'],
            methods=backend_api.routes[route]['methods'],
        )

    server = gevent.pywsgi.WSGIServer((host_, port), app, log=logging.getLogger())
    server.serve_forever()


if __name__ == "__main__":
    run_app(local=True)
