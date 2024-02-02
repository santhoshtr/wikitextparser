from typing import List, Optional

import lark
from babel import Locale

from wikitextparser.ast.base import Meta, Node, Tree


class PluralNode(Tree):
    NAME = "plural"

    def __init__(self, name: str, children: List[Node] = None, meta: Optional[Meta] = None):
        super().__init__(name, children, meta)
        self._placeholder = None
        self._forms: tuple[str | None, str] = None
        self.form = None

    @property
    def placeholder(self) -> str:
        if self._placeholder:
            return self._placeholder
        return str(self.children[0].value)

    def i18n(self, locale, params):
        key = int(self.placeholder)
        pluralForms = list(Locale(locale).plural_form.tags)
        pluralForms.append("other")
        form_index = pluralForms.index(Locale(locale).plural_form(key))
        print(f"form_index: {form_index}")
        for form_name, form_value in self.forms:
            if form_name is not None and int(form_name) == key:
                self.form = form_value
                return

        form_values = []
        for form_name, form_value in self.forms:
            if not form_name:
                form_values.append(form_value)
        self.form = form_values[min(form_index, len(form_values) - 1)]
        if self.forms is None:
            self.form = form_values[:-1]
        return lark.Tree("expanded", self.form)

    @property
    def forms(self) -> str:
        if self._forms:
            return self._forms
        params_tree = self.children[1:]
        forms = []
        for form_tree in params_tree:
            form_name = None

            if len(form_tree.children) == 2:
                form_name_tree = form_tree.children[0]
                form_value_tree = form_tree.children[1]
            else:
                form_value_tree = form_tree.children[0]
                form_name_tree = None

            if form_name_tree:
                form_name = form_name_tree.children[0].value
            form_value = form_value_tree.children
            forms.append((form_name, form_value))
        return forms

    def to_plaintext(self):
        self._placeholder = "0"
        return self.i18n("en", [0])
