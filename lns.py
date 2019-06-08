import redis
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from utils import genereate_random_string, validate_url

app = Flask(__name__)

r = redis.StrictRedis(os.environ.get('REDIS_HOST', 'localhost'))
app.url_map.strict_slashes = False


@app.route('/', methods=['GET'])
def index():
    return render_template('index.jinja2')


@app.route('/<uid>', methods=['GET'])
def redirect_to_url(uid):
    url = r.get(uid + ':url')

    if url is not None:
        return redirect(url.decode('utf-8'))
    else:
        return render_template('index.jinja2', link='None')


@app.route('/<uid>/show', methods=['GET'])
def show(uid):
    link = r.get(uid + ':url')

    if link is not None:
        return render_template('index.jinja2', link=url_for('redirect_to_url', uid=uid,
                                                            _external=True))
    else:
        return render_template('index.jinja2', link='None')


@app.route('/', methods=['POST'])
def store():
    url = request.form['url']

    wants_json = request.headers['Accept'] == 'application/json'

    if url is not None and len(url) > 0:
        if not validate_url(url):
            return render_template('index.jinja2', url=url, error='Given URL is not valid!')

        while True:
            uid = genereate_random_string(6)

            if r.get(uid + ':url') is None:
                break

        r.set(uid + ':url', url)

        if wants_json:
            return jsonify({'status': 'ok', 'message': '', 'data': {
                'url': url_for('redirect_to_url', uid=uid, _external=True),
                'address_bar': url_for('show', uid=uid, _external=True)}})
        else:
            ret = redirect(url_for('show', uid=uid))
    else:
        if wants_json:
            return jsonify({'status': 'error', 'message': 'empty_url', 'data': {}})
        else:
            ret = render_template('index.jinja2', error='URL cannot be empty!')

    return ret


if __name__ == '__main__':
    app.run()
