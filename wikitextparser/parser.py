from pathlib import Path

import lark
from lark.reconstruct import Reconstructor


class WikiTextParser:
    def __init__(
        self,
        grammar_text=None,
        start: str = "start",
    ) -> None:
        if not grammar_text:
            grammar_path: Path = Path(Path(__file__).parent.absolute() / "wiki.lark")
            with grammar_path.open("rt") as f:
                grammar_text = f.read()

        self.lark = lark.Lark(
            grammar_text,
            start=start,
            parser="lalr",
            regex=True,
            # debug=True,
            maybe_placeholders=False,  # Necessary for reconstructor
        )

    def parse(self, wikitext: str) -> lark.ParseTree:
        return self.lark.parse(wikitext)

    def transform(self, transformer, tree):
        ast = transformer.transform(tree)
        return ast

    def reconstruct(self, ast):
        new_text = Reconstructor(self.lark).reconstruct(ast)
        new_text = new_text.replace("🧩", "")
        return new_text

    def print_as_image(self, tree, filename="ast.svg"):
        graph = lark.tree.pydot__tree_to_graph(tree)
        print(filename)
        with open(filename, "wb") as svg_file:
            svg_file.write(graph.create_svg())
            svg_file.close()
