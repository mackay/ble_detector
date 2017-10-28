from bottle import static_file, route
from bottle import view

import logging
log = logging.getLogger()


@route('/')
@view('menu')
def static_index():
    return dict()


@route('/<filename:path>')
def all_static(filename):
    return static_file(filename, root='./server/static')
