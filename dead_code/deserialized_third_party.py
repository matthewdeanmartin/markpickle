"""
The vendorized version of CommonMark is not compatible with recent versions of python.

The Commonmark library is unmaintained.

The "successor", markdown-it-py, is so different from the early common mark, it is a lot of
work to update to latest.
"""
from markdown_to_json.markdown_to_json import CMarkASTNester, Renderer
from markdown_to_json.vendor import CommonMark


def deserialize_to_nested(value: str):
    ast = CommonMark.DocParser().parse(value)
    nested_ast = CMarkASTNester().nest(ast)

    stringified = Renderer().stringify_dict(nested_ast)
    return stringified
