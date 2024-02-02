from lark import Transformer, v_args

from .ast import Leaf, Nodes, Tree


@v_args(meta=True)
class LarkToWikiTransformer(Transformer):
    def __init__(self, cb=None, cb_params=None) -> None:
        if cb_params is None:
            cb_params = []
        super().__init__()
        self.cb = cb
        self.cb_params = cb_params

    def __default__(self, data, children, meta):
        """Default function that is called if there is no attribute matching ``data``

        """
        cls = Nodes.registry.get(data.value, Tree)
        w_node = cls(data.value, children, meta)
        return self.do_operation(w_node)

    def do_operation(self, w_node):
        if self.cb:
            if hasattr(w_node, self.cb):
                operation = getattr(w_node, self.cb)
                return operation(*self.cb_params)

        return w_node.to_lark()

    def __default_token__(self, token):
        """Default function that is called if there is no attribute matching ``token.type``

        Can be overridden. Defaults to returning the token as-is.
        """
        # FIXME, token has Meta attributes, capture and pass to Leaf
        cls = Nodes.registry.get(token.type, Leaf)
        w_token = cls(token.type, token.value)
        return self.do_operation(w_token)
