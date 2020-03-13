from abc import ABCMeta, abstractmethod as abstract_method
from json.encoder import JSONEncoder as BaseJsonEncoder
from typing import Iterable, Mapping


class JsonSerializable(object, metaclass=ABCMeta):
    """
    Interface for classes that can be safely converted to JSON.
    """

    @abstract_method
    def as_json_compatible(self):
        """
        Returns a JSON-compatible representation of the object.

        References:

        - :py:class:`iota.json.JsonEncoder`.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def _repr_pretty_(self, p, cycle):
        """
        Makes JSON-serializable objects play nice with IPython's default
        pretty-printer.

        Sadly, :py:func:`pprint.pprint` does not have a similar
        mechanism.

        References:

        - http://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html
        - :py:meth:`IPython.lib.pretty.RepresentationPrinter.pretty`
        - :py:func:`pprint._safe_repr`
        """
        class_name = type(self).__name__

        if cycle:
            p.text('{cls}(...)'.format(
                cls=class_name,
            ))
        else:
            with p.group(
                    len(class_name) + 1,
                    '{cls}('.format(cls=class_name),
                    ')',
            ):
                prepared = self.as_json_compatible()

                if isinstance(prepared, Mapping):
                    p.text('**')
                elif isinstance(prepared, Iterable):
                    p.text('*')

                p.pretty(prepared)


class JsonEncoder(BaseJsonEncoder):
    """
    JSON encoder with support for :py:class:`JsonSerializable`.
    """

    def default(self, o):
        if isinstance(o, JsonSerializable):
            return o.as_json_compatible()

        return super(JsonEncoder, self).default(o)
