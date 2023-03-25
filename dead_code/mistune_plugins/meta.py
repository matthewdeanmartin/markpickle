import re

# r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)'
# ^([^:]*):(.*)$
BLOCK_META_PATTERN = re.compile(r"[ ]{0,3}^[^\n:]*:[^\n]*$")


def render_ast_meta_item(children, level, checked):
    return {
        "type": "task_list_item",
        "children": children,
        "level": level,
        "checked": checked,
    }


# def meta(md):
#     md.before_render_hooks.append(task_lists_hook)
#
#     if md.renderer.NAME == 'ast':
#         md.renderer.register('meta', render_ast_task_list_item)


def meta(md):
    md.block.register_rule("block_meta", BLOCK_META_PATTERN, parse_block_meta)  # , before='list')
    md.block.rules.append("block_meta")
    # md.inline.register('inline_math', INLINE_MATH_PATTERN, parse_inline_math, before='link')
    # if md.renderer and md.renderer.NAME == 'html':
    #     md.renderer.register('block_math', render_block_math)
    # md.renderer.register('inline_math', render_inline_math)


def parse_block_meta(block, m, state):
    # text = m.group('meta_text')
    key, value = m.group(1), m.group(2)
    # use ``state.append_token`` to save parsed block math token
    # state.append_token()
    # 'raw': f"{key}:{value}",
    return {"type": "block_meta", "text": "yo!", "key": key, "value": value}
    # return the end position of parsed text
    # since python doesn't count ``$``, we have to +1
    # if the pattern is not ended with `$`, we can't +1
    # return m.end() + 1


# """
# Meta Data Extension for Python-Markdown
# =======================================
#
# This extension adds Meta Data handling to markdown.
#
# See <https://Python-Markdown.github.io/extensions/meta_data>
# for documentation.
#
# Original code Copyright 2007-2008 [Waylan Limberg](http://achinghead.com).
#
# All changes Copyright 2008-2014 The Python Markdown Project
#
# License: [BSD](https://opensource.org/licenses/bsd-license.php)
#
# """
#
# # from . import Extension
# # from ..preprocessors import Preprocessor
# import re
# import logging
#
# # log = logging.getLogger('MARKDOWN')
#
# # Global Vars
# META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
# META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')
# BEGIN_RE = re.compile(r'^-{3}(\s.*)?')
# END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')
#
#
# class MetaExtension (Extension):
#     """ Meta-Data extension for Python-Markdown. """
#
#     def extendMarkdown(self, md):
#         """ Add MetaPreprocessor to Markdown instance. """
#         md.registerExtension(self)
#         self.md = md
#         md.preprocessors.register(MetaPreprocessor(md), 'meta', 27)
#
#     def reset(self):
#         self.md.Meta = {}
#
#
# class MetaPreprocessor(Preprocessor):
#     """ Get Meta-Data. """
#
#     def run(self, lines):
#         """ Parse Meta-Data and store in Markdown.Meta. """
#         meta = {}
#         key = None
#         if lines and BEGIN_RE.match(lines[0]):
#             lines.pop(0)
#         while lines:
#             line = lines.pop(0)
#             m1 = META_RE.match(line)
#             if line.strip() == '' or END_RE.match(line):
#                 break  # blank line or end of YAML header - done
#             if m1:
#                 key = m1.group('key').lower().strip()
#                 value = m1.group('value').strip()
#                 try:
#                     meta[key].append(value)
#                 except KeyError:
#                     meta[key] = [value]
#             else:
#                 m2 = META_MORE_RE.match(line)
#                 if m2 and key:
#                     # Add another line to existing key
#                     meta[key].append(m2.group('value').strip())
#                 else:
#                     lines.insert(0, line)
#                     break  # no meta data - done
#         self.md.Meta = meta
#         return lines
#
#
# def makeExtension(**kwargs):  # pragma: no cover
#     return MetaExtension(**kwargs)

if __name__ == "__main__":
    import mistune

    string_value = """Title:   My Document
Summary: A brief description of my document.
Authors: Waylan Limberg
         John Doe
Date:    October 2, 2007
blank-value:
base_url: http://example.com

This is the first paragraph of the document.
    """

    parser = mistune.create_markdown(renderer="ast", plugins=[meta])

    result = parser.parse(string_value)
    print(result)
