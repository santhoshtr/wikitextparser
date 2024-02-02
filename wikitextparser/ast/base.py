from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import List, Optional

import lark

from .registry import Nodes


class Node(ABC, metaclass=Nodes):
    """The Node interface sets the common method for all nodes."""

    @abstractmethod
    def to_lark(self) -> str:
        """The operation method needs to be implemented by Leaf and Tree classes."""
        pass


class Meta:
    empty: bool
    line: int
    column: int
    start_pos: int
    end_line: int
    end_column: int
    end_pos: int

    def __init__(self):
        self.empty = True


class Leaf(Node):
    """Leaf represents individual objects that don’t contain other elements."""

    def __init__(self, name: str, value: str = None):
        self.name = name
        if not value:
            value = self.name
        self.value = value

    def __repr__(self):
        return f"{self.name} → {self.value}"

    def to_lark(self):
        return lark.Token(self.name, self.value)


class Tree(Node):
    """Tree acts as a container that can hold both Leaf and other Tree instances."""

    def __init__(self, name: str, children: List[Node] = None, meta: Optional[Meta] = None):
        if children is None:
            children = []
        self.name = name
        self._meta = meta
        self.children: List[Node] = children

    @property
    def meta(self) -> Meta:
        if self._meta is None:
            self._meta = Meta()
        return self._meta

    def add(self, node: Node):
        """Method to add elements to the Tree."""
        self.children.append(node)

    def remove(self, node: Node):
        """Method to remove elements from the Tree."""
        self.children.remove(node)

    def _pretty_label(self):
        return self.name

    def _pretty(self, level, indent_str):
        yield f"{indent_str*level}{self._pretty_label()}"
        if len(self.children) == 1 and not isinstance(self.children[0], Tree):
            yield f"\t{self.children[0]}\n"
        else:
            yield "\n"
            for n in self.children:
                if isinstance(n, Tree):
                    yield from n._pretty(level + 1, indent_str)
                else:
                    yield f"{indent_str*(level+1)}{n}\n"

    def pretty(self, indent_str: str = "  ") -> str:
        """Returns an indented string representation of the tree.

        Great for debugging.
        """
        return "".join(self._pretty(0, indent_str))

    def __repr__(self):
        return "Tree(%r, %r)" % (self.name, self.children)

    def __rich__(self, parent: Optional["rich.tree.Tree"] = None) -> "rich.tree.Tree":  # noqa: F821
        """Returns a tree widget for the 'rich' library.

        Example:
            ::
                from rich import print
                from lark import Tree

                tree = Tree('root', ['node1', 'node2'])
                print(tree)
        """
        return self._rich(parent)

    def _rich(self, parent):
        if parent:
            tree = parent.add(f"[bold]{self.name}[/bold]")
        else:
            import rich.tree

            tree = rich.tree.Tree(self.name)

        for c in self.children:
            if isinstance(c, Tree):
                c._rich(tree)
            else:
                tree.add(f"[green]{c}[/green]")

        return tree

    def __eq__(self, other):
        try:
            return self.name == other.name and self.children == other.children
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.children)))

    def iter_subtrees(self):
        """Depth-first iteration.

        Iterates over all the subtrees, never returning to the same node
        twice (Lark's parse-tree is actually a DAG).
        """
        queue = [self]
        subtrees = OrderedDict()
        for subtree in queue:
            subtrees[id(subtree)] = subtree
            # Reason for type ignore https://github.com/python/mypy/issues/10999
            queue += [
                c
                for c in reversed(subtree.children)  # type: ignore[misc]
                if isinstance(c, Tree) and id(c) not in subtrees
            ]

        del queue
        return reversed(list(subtrees.values()))

    def iter_subtrees_topdown(self):
        """Breadth-first iteration.

        Iterates over all the subtrees, return nodes in order like pretty() does.
        """
        stack = [self]
        stack_append = stack.append
        stack_pop = stack.pop
        while stack:
            node = stack_pop()
            if not isinstance(node, Tree):
                continue
            yield node
            for child in reversed(node.children):
                stack_append(child)

    def to_graph(self, rankdir="LR", **kwargs):
        """Creates a colorful image that represents the tree (data+children, without meta)

        Possible values for `rankdir` are "TB", "LR", "BT", "RL", corresponding to
        directed graphs drawn from top to bottom, from left to right, from bottom to
        top, and from right to left, respectively.

        `kwargs` can be any graph attribute (e. g. `dpi=200`). For a list of
        possible attributes, see https://www.graphviz.org/doc/info/attrs.html.
        """

        import pydot

        graph = pydot.Dot(graph_type="digraph", rankdir=rankdir, **kwargs)

        i = [0]

        def new_leaf(leaf):
            node = pydot.Node(i[0], label=repr(leaf))
            i[0] += 1
            graph.add_node(node)
            return node

        def _to_pydot(subtree):
            color = hash(subtree.name) & 0xFFFFFF
            color |= 0x808080

            subnodes = [
                _to_pydot(child) if isinstance(child, Tree) else new_leaf(child)
                for child in subtree.children
            ]
            node = pydot.Node(i[0], style="filled", fillcolor="#%x" % color, label=subtree.name)
            i[0] += 1
            graph.add_node(node)

            for subnode in subnodes:
                graph.add_edge(pydot.Edge(node, subnode))

            return node

        _to_pydot(self)

        return graph

    def to_lark(self):
        return lark.tree.Tree(self.name, self.children, self.meta)
