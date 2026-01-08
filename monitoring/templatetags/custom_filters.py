from django import template

register = template.Library()

@register.filter
def format_number(value):
    """Format a number with commas for thousands separator."""
    try:
        # Convert to float first, then to int if it's a whole number
        num = float(value)
        if num == int(num):
            return "{:,.0f}".format(int(num))
        else:
            return "{:,.2f}".format(num)
    except (ValueError, TypeError):
        return value
