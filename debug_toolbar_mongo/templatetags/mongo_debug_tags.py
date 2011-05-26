from django import template

import pprint

register = template.Library()

@register.filter
def format_dict(value, width=60):
    return pprint.pformat(value, width=int(width))

@register.filter
def highlight_json(value):
    try:
        from pygments import highlight
        from pygments.lexers import JavascriptLexer
        from pygments.formatters import HtmlFormatter
    except ImportError:
        return value
    # Can't use class-based colouring because the debug toolbar's css rules
    # are more specific so take precedence
    formatter = HtmlFormatter(style='friendly', nowrap=True, noclasses=True)
    return highlight(value, JavascriptLexer(), formatter)
