from django.template.loader import render_to_string

import pprint
import functools
import time

import pymongo.collection
import pymongo.cursor
from debug_toolbar.panels import DebugPanel


class MongoOperationHook(object):
    """Track operations sent to MongoDB via PyMongo.
    """

    def __init__(self):
        self.queries = []
        self.active = False

    def install(self):
        self.original_methods = {
            'insert': pymongo.collection.Collection.insert,
            'update': pymongo.collection.Collection.update,
            'remove': pymongo.collection.Collection.remove,
            'refresh': pymongo.cursor.Cursor._refresh,
        }

        # Wrap Cursor._refresh for getting queries
        @functools.wraps(self.original_methods['refresh'])
        def cursor_refresh(cursor_self):
            # Look up __ private instance variables
            def privar(name):
                return getattr(cursor_self, '_Cursor__{0}'.format(name))

            if not self.active or privar('id') is not None:
                # Inactive or getMore - move on
                return self.original_methods['refresh'](cursor_self)

            query_details = {
                'options': privar('query_options')(),
                'collection_name': privar('collection').full_name,
                'num_to_skip': privar('skip'),
                'num_to_return': privar('limit'),
                'query': privar('query_spec')(),
                'field_selector': privar('fields'),
            }

            # Time the actual query
            start_time = time.time()
            result = self.original_methods['refresh'](cursor_self)
            total_time = (time.time() - start_time) * 1000

            self.queries.append({
                'type': 'query',
                'query': query_details['query'].to_dict(),
                'collection': query_details['collection_name'],
                'time': total_time,
            })

            return result

        pymongo.cursor.Cursor._refresh = cursor_refresh

    def uninstall(self):
        pymongo.cursor.Cursor._refresh = self.original_methods['refresh']

    def reset(self):
        self.queries = []

    def start(self):
        self.active = True

    def stop(self):
        self.active = False


class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB queries.
    """
    name = 'MongoDB'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.op_hook = MongoOperationHook()
        self.op_hook.install()

    def process_request(self, request):
        self.op_hook.reset()
        self.op_hook.start()

    def process_response(self, request, response):
        self.op_hook.stop()

    def nav_title(self):
        return 'MongoDB'

    def nav_subtitle(self):
        num_queries = len(self.op_hook.queries)
        return '{0} queries executed'.format(num_queries)

    def title(self):
        return 'MongoDB Queries'

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context['queries'] = self.op_hook.queries
        return render_to_string('mongo-panel.html', context)


