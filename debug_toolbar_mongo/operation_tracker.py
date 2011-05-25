import functools
import time

import pymongo.collection
import pymongo.cursor


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

            query_son = privar('query_spec')()

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
            else:
                # Normal Query
                query_data['skip'] = privar('skip')
                query_data['limit'] = privar('limit')
                query_data['query'] = query_son['$query']
                query_data['ordering'] = self._get_ordering(query_son)

            self.queries.append(query_data)

            return result

        pymongo.cursor.Cursor._refresh = cursor_refresh

    def _get_ordering(self, son):
        def fmt(field, direction):
            return '{0}{1}'.format({-1: '-', 1: '+'}[direction], field)

        if '$orderby' in son:
            return ', '.join(fmt(f, d) for f, d in son['$orderby'].items())

    def uninstall(self):
        pymongo.cursor.Cursor._refresh = self.original_methods['refresh']

    def reset(self):
        self.queries = []

    def start(self):
        self.active = True

    def stop(self):
        self.active = False
