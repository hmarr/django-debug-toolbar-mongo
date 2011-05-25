from django.template.loader import render_to_string

import pprint
import functools
import time

import pymongo.collection
import pymongo.cursor
from debug_toolbar.panels import DebugPanel


class MongoOperationTracker(object):
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

            # NOTE: See pymongo/cursor.py+557 [_refresh()] and
            # pymongo/message.py for where information is stored

            # Time the actual query
            start_time = time.time()
            result = self.original_methods['refresh'](cursor_self)
            total_time = (time.time() - start_time) * 1000

            query_son = privar('query_spec')().to_dict()

            query_data = {
                'time': total_time,
                'operation': 'query',
            }

            # Collection in format <db_name>.<collection_name>
            collection_name = privar('collection')
            query_data['collection'] = collection_name.full_name.split('.')[1]

            if query_data['collection'] == '$cmd':
                query_data['operation'] = 'command'
                # Handle count as a special case
                if 'count' in query_son:
                    # Information is in a different format to a standar query
                    query_data['collection'] = query_son['count']
                    query_data['operation'] = 'count'
                    query_data['skip'] = query_son.get('skip')
                    query_data['limit'] = query_son.get('limit')
                    query_data['query'] = query_son['query']
                    del query_son['count']
            else:
                # Normal Query
                query_data['skip'] = privar('skip')
                query_data['limit'] = privar('limit')
                query_data['query'] = query_son['$query']

            self.queries.append(query_data)

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
        self.op_tracker = MongoOperationTracker()
        self.op_tracker.install()

    def process_request(self, request):
        self.op_tracker.reset()
        self.op_tracker.start()

    def process_response(self, request, response):
        self.op_tracker.stop()

    def nav_title(self):
        return 'MongoDB'

    def nav_subtitle(self):
        num_queries = len(self.op_tracker.queries)
        total_time = sum(q['time'] for q in self.op_tracker.queries)
        return '{0} operations in {1:.2f}ms'.format(num_queries, total_time)

    def title(self):
        return 'MongoDB Queries'

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context['queries'] = self.op_tracker.queries
        return render_to_string('mongo-panel.html', context)


