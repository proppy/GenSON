from .base import SchemaStrategy


class BaseArray(SchemaStrategy):
    """
    abstract array schema strategy
    """
    KEYWORDS = ('type', 'items')

    @staticmethod
    def match_object(obj):
        return isinstance(obj, list)

    def to_schema(self):
        schema = super(BaseArray, self).to_schema()
        schema['type'] = 'array'
        if self._items:
            schema['items'] = self.items_to_schema()
        return schema


class List(BaseArray):
    """
    strategy for list-style array schemas. This is the default
    strategy for arrays.
    """
    @staticmethod
    def match_schema(schema):
        return schema.get('type') == 'array' \
            and isinstance(schema.get('items', {}), dict)

    def __init__(self, node_class):
        super(List, self).__init__(node_class)
        self._items = node_class()

    def add_schema(self, schema):
        self.add_extra_keywords(schema)
        if 'items' in schema:
            self._items.add_schema(schema['items'])

    def add_object(self, obj, examples=False):
        for item in obj:
            self._items.add_object(item, examples)

    def items_to_schema(self):
        return self._items.to_schema()


class Tuple(BaseArray):
    """
    strategy for tuple-style array schemas. These will always have
    an items key to preserve the fact that it's a tuple.
    """
    @staticmethod
    def match_schema(schema):
        return schema.get('type') == 'array' \
            and isinstance(schema.get('items'), list)

    def __init__(self, node_class):
        super(Tuple, self).__init__(node_class)
        self._items = [node_class()]

    def add_schema(self, schema):
        self.add_extra_keywords(schema)
        if 'items' in schema:
            self._add(schema['items'], lambda s, i: s.add_schema(i))

    def add_object(self, obj, examples=False):
        self._add(obj, lambda s, i: s.add_object(i, examples))

    def _add(self, items, func):
        while len(self._items) < len(items):
            self._items.append(self.node_class())

        for subschema, item in zip(self._items, items):
            func(subschema, item)

    def items_to_schema(self):
        return [item.to_schema() for item in self._items]
