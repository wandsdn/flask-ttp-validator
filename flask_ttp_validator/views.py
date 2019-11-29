""" A flask webserver to validate a Table Type Pattern.
"""

# Copyright 2019 Richard Sanger, Wand Network Research Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import time
import traceback
import os
import json
import re
import io
import hashlib

from flask import render_template, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ttp_tools.TTP import TableTypePattern
from ttp_tools.validate_ttp import generate_listing, sort_issues
from flask_ttp_validator import app


app.config.from_pyfile('ttp-validator.cfg')
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

limiter = Limiter(app, key_func=get_remote_address)
my_logger = logging.getLogger('test')
my_logger.addHandler(logging.NullHandler())
my_logger.setLevel(logging.WARNING)
my_logger.propagate = 0


@app.route('/')
def index_page():
    return render_template("TTPValidator.html")

def error_response(message, status_code=400):
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


valid_cache_key = re.compile(r"^[0-9a-f]+\Z")

def generate_cache_key(u_source):
    cache_key = hashlib.sha256(u_source.encode('utf-8')).hexdigest()
    return cache_key


def check_cache(cache_key):
    path = os.path.join(app.config['CACHE_DIR'], cache_key)
    try:
        if os.path.isdir(path):
            response = os.path.join(path, "result.html")
            with io.open(response, 'r', encoding='utf-8') as res:
                return res.read()
        return None
    except Exception:
        return None


def save_cache(cache_key, u_source, res):
    path = os.path.join(app.config['CACHE_DIR'], cache_key)
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            source_path = os.path.join(path, "source.json")
            result_path = os.path.join(path, "result.html")

            with io.open(source_path, 'w', encoding='utf-8') as fout:
                fout.write(u_source)
            with io.open(result_path, 'w', encoding='utf-8') as fout:
                fout.write(res)
            return True
        except Exception:
            return False
    else:
        return False


def save_error(cache_key, u_source, error):
    error = type(u'')(error)
    path = os.path.join(app.config['CACHE_DIR'], cache_key)
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            source_path = os.path.join(path, "source.json")
            error_path = os.path.join(path, "error.txt")

            with io.open(source_path, 'w', encoding='utf-8') as fout:
                fout.write(u_source)
            with io.open(error_path, 'w', encoding='utf-8') as fout:
                fout.write(error)
            return True
        except Exception:
            return False
    else:
        return False


@app.route('/p/<cache_key>', methods=['GET'])
def server_permalink(cache_key):
    # Validate this
    if re.match(valid_cache_key, cache_key):
        cached = check_cache(cache_key)
        if cached:
            return cached
    abort(404)


@app.route('/check/', methods=['POST'])
@limiter.limit("2 per 30 seconds")
def check():
    start_t = time.time()
    source = None

    if 'TTPFile' in request.files and request.files['TTPFile'].filename:
        # Validate the TTPFile
        source = request.files['TTPFile'].read()
    elif 'TTP' in request.form:
        source = request.form['TTP']
    if not source:
        abort(400, "No input TTP was included with the request.")
    if isinstance(source, type(u'')):
        u_source = source
    else:
        # JSON should be in UTF-8, 16, or 32. Most likely UTF-8.
        u_source = None
        for codec in ['utf-8', 'utf-16', 'utf-32']:
            try:
                u_source = source.decode(codec)
                break
            except UnicodeError:
                pass
        else:
            abort(400,
                  u"Bad encoding expecting utf-8, utf-16 or utf-32")

    if 'prettify' in request.form:
        try:
            parsed = json.loads(u_source)
            u_source = json.dumps(parsed, ensure_ascii=False, indent=4)
        except Exception as e:
            cache_key = generate_cache_key(u_source)
            save_error(cache_key, u_source, traceback.format_exc())
            abort(400, u"Failed to decode the TTP as JSON. Please check the"
                       u" TTP is valid JSON using a JSON validator. "
                       u"Error Message: %s" % (str(e)))

    cache_key = generate_cache_key(u_source)
    cached = check_cache(cache_key)
    if cached:
        return cached

    try:
        ttp = TableTypePattern(u_source, logger=my_logger,
                               track_orig=True, as_unicode=True)
    except ValueError as e:
        save_error(cache_key, u_source, traceback.format_exc())
        abort(400, u"Failed to decode the TTP as JSON. Please check the TTP"
                   u" is valid JSON using a JSON validator. "
                   u"Error Message: %s" % (str(e)))
    except Exception as e:
        save_error(cache_key, u_source, traceback.format_exc())
        abort(500, u"Internal validator error when processing the TTP. This is"
                   u" most likely caused by invalid data in the TTP. "
                   u"You have encountered an internal bug where said"
                   u" invalid data is not handled gracefully."
                   u" Send me a copy and I'll look into fixing it.")

    sort_issues(ttp.issues)

    gen_ms = int((time.time() - start_t)*1000)
    result = render_template("ResultPage.html", issues=ttp.issues,
                             source=u_source,
                             FILE=generate_listing(ttp.issues, u_source),
                             gen_ms=gen_ms,
                             permalink=("../p/"+cache_key))
    save_cache(cache_key, u_source, result)
    return result
