# class MarkdownElement:
#     def validate(self, element):
#         raise NotImplementedError
#
#
# class Title(MarkdownElement):
#     def validate(self, element):
#         # Check if element is H1 heading
#         return element["level"] == 1
#
#
# class Subtitle(MarkdownElement):
#     def validate(self, element):
#         # Check if element is H2 heading
#         return element["level"] == 2
#
#
# class Paragraph(MarkdownElement):
#     def validate(self, element):
#         # Check if element is a paragraph
#         return element["type"] == "paragraph"
#
#
# class List(MarkdownElement):
#     def validate(self, element):
#         # Check if element is a list
#         return element["type"] == "list"
#
#
# class MarkdownSchema:
#     def __init__(self, elements: List[MarkdownElement]):
#         self.elements = elements
#
#     def validate(self, markdown):
#         markdown_elements = mistune.parse(markdown)
#         if len(markdown_elements) != len(self.elements):
#             return False
#         for schema_element, markdown_element in zip(self.elements, markdown_elements):
#             if not schema_element.validate(markdown_element):
#                 return False
#         return True
#
#
# import mistune
# from typing import List
#
#
# class MarkdownElement:
#     def validate(self, element):
#         raise NotImplementedError
#
#
# class Title(MarkdownElement):
#     def validate(self, element):
#         # Check if element is H1 heading
#         return element["level"] == 1
#
#
# class Subtitle(MarkdownElement):
#     def validate(self, element):
#         # Check if element is H2 heading
#         return element["level"] == 2
#
#
# class Paragraph(MarkdownElement):
#     def validate(self, element):
#         # Check if element is a paragraph
#         return element["type"] == "paragraph"
#
#
# class List(MarkdownElement):
#     def validate(self, element):
#         # Check if element is a list
#         return element["type"] == "list"
#
#
# class MarkdownSchema:
#     def __init__(self, elements: List[MarkdownElement]):
#         self.elements = elements
#
#     def validate(self, markdown):
#         markdown_elements = mistune.parse(markdown)
#         if len(markdown_elements) != len(self.elements):
#             return False
#         for schema_element, markdown_element in zip(self.elements, markdown_elements):
#             if not schema_element.validate(markdown_element):
#                 return False
#         return True
