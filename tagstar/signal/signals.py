from django.dispatch import Signal

item_tagged = Signal(providing_args=["sender", "action", "content_type", "instance", "tags"])
