from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

import pymongo

conn = pymongo.Connection()
db = conn.debug_test

def index(request):
    list(db.test.find({'name': 'test'}))
    list(db.test.find({'name': 'test'}).skip(1))
    db.test.find({'name': 'test'}).count()
    db.test.find({'name': 'test'}).skip(1).count(with_limit_and_skip=True)
    list(db.test.find({'name': 'test'}).sort('name'))
    sort_fields = [('name', pymongo.DESCENDING), ('date', pymongo.ASCENDING)]
    list(db.test.find({'name': 'test'}).sort(sort_fields))
    return render_to_response('index.html')

