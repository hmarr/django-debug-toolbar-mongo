from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from debug_toolbar.panels import DebugPanel

import operation_tracker

_NAV_SUBTITLE_TPL = u'''
{% for o, n, t in operations %}
    {{ n }} {{ o }}{{ n|pluralize }} in {{ t }}ms<br/>

    {% if forloop.last and forloop.counter0 %}
        {{ count }} operation{{ count|pluralize }} in {{ time }}ms
    {% endif %}
{% endfor %}
'''

class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations.
    """
    name = 'MongoDB'
    has_content = True
    template = 'mongo-panel.html'

    def __init__(self, *args, **kwargs):
        super(MongoDebugPanel, self).__init__(*args, **kwargs)
        operation_tracker.install_tracker()

    def process_request(self, request):
        operation_tracker.reset()

    def nav_title(self):
        return 'MongoDB'

    def nav_subtitle(self):
        fun = lambda x, y: (x, len(y), '%.2f' % sum(z['time'] for z in y))
        ctx = {'operations': [], 'count': 0, 'time': 0}

        if operation_tracker.queries:
            ctx['operations'].append(fun('read', operation_tracker.queries))
            ctx['count'] += len(operation_tracker.queries)
            ctx['time'] += sum(x['time'] for x in operation_tracker.queries)

        if operation_tracker.inserts:
            ctx['operations'].append(fun('insert', operation_tracker.inserts))
            ctx['count'] += len(operation_tracker.inserts)
            ctx['time'] += sum(x['time'] for x in operation_tracker.inserts)

        if operation_tracker.updates:
            ctx['operations'].append(fun('update', operation_tracker.updates))
            ctx['count'] += len(operation_tracker.updates)
            ctx['time'] += sum(x['time'] for x in operation_tracker.updates)

        if operation_tracker.removes:
            ctx['operations'].append(fun('remove', operation_tracker.removes))
            ctx['count'] += len(operation_tracker.removes)
            ctx['time'] += sum(x['time'] for x in operation_tracker.removes)

        ctx['time'] = '%.2f' % ctx['time']

        return mark_safe(Template(_NAV_SUBTITLE_TPL).render(Context(ctx)))

    def title(self):
        return 'MongoDB Operations'

    def url(self):
        return ''

    def process_response(self, request, response):
        self.record_stats({
            'queries': operation_tracker.queries,
            'inserts': operation_tracker.inserts,
            'updates': operation_tracker.updates,
            'removes': operation_tracker.removes
        })
