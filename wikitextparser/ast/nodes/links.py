from typing import List, Optional

import lark

from wikitextparser.ast.base import Meta, Node, Tree


class WikiLinkNode(Tree):
    NAME = "wikilink"

    def __init__(self, name: str, children: List[Node] = None, meta: Optional[Meta] = None):
        super().__init__(name, children, meta)
        self._title = None
        self._link_text = None

    @property
    def title(self) -> str:
        if self._title:
            return self._title
        if len(self.children) == 2:
            [title_tree, _] = self.children
            return title_tree.children[0].value

        if len(self.children) == 1:
            [title_tree] = self.children
            return title_tree.children[0].value

    @property
    def link_text(self) -> str:
        if self._link_text:
            return self._link_text
        if len(self.children) == 2:
            [_, text_token] = self.children
            return text_token.value

        return None

    def to_plaintext(self):
        return lark.Token("TEXT", self.link_text or self.title)


class ExternalLinkNode(Tree):
    NAME = "externallink"

    def __init__(self, name: str, children: List[Node] = None, meta: Optional[Meta] = None):
        super().__init__(name, children, meta)
        self._url = None
        self._link_text = None

    @property
    def url(self) -> str:
        if self._url:
            return self._url
        if len(self.children) == 3:
            [url_token, _, _] = self.children
            return url_token.value

        if len(self.children) == 1:
            [url_token] = self.children
            return url_token.value

    @property
    def link_text(self) -> str:
        if self._link_text:
            return self._link_text

        if len(self.children) == 3:
            [_, _, text_token] = self.children
            return text_token.value

        return None

    def to_plaintext(self):
        return lark.Token("TEXT", self.link_text or self.url)
