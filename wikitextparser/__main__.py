import sys
from pathlib import Path

import lark
import rich

from wikitextparser.parser import WikiTextParser
from wikitextparser.transformer import LarkToWikiTransformer

if __name__ == "__main__":
    grammar_path: Path = Path(Path(__file__).parent.absolute() / "wiki.lark")
    with grammar_path.open("rt") as f:
        grammar_text = f.read()
    parser = WikiTextParser(grammar_text)

    with open(sys.argv[1]) as text_file:
        text = text_file.read()
    lark_ast = parser.parse(text)
    rich.print(lark_ast)
    parser.print_as_image(lark_ast)

    transformer: lark.Transformer = LarkToWikiTransformer(cb="i18n", cb_params=["en", [0]])
    transformer: lark.Transformer = LarkToWikiTransformer(cb="to_plaintext")
    transformed_ast = parser.transform(transformer, lark_ast)
    rich.print(transformed_ast)
    rich.inspect(transformed_ast)
    parser.print_as_image(transformed_ast, "transformed.ast.png")
    print(parser.reconstruct(transformed_ast))
