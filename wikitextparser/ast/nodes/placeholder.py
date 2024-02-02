import lark

from wikitextparser.ast.base import Leaf


class PlaceholderNode(Leaf):
    NAME = "PLACEHOLDER"

    def __init__(self, name: str, value: str):
        super().__init__(name, value)
        self.placeholder = value
        self.resolved_value = None

    @staticmethod
    def get_index(placeholder):
        return int(placeholder.replace("$", ""))

    def i18n(self, locale, params):
        self.resolved_value = params[self.get_index(self.placeholder)]
        return lark.Token("TEXT", self.resolved_value)

    def to_plaintext(self):
        return self.i18n("en", [0])
