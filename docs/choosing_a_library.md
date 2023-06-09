# Choosing a library

## You need to get data out of a predictable, data-like markdown document
For example, if it has only headers, lists and tables. Use markpickle. It will usually work.

## You want to create a more human-readable, human-writable format or used markdown tools
You could use markpickle if you are okay with the constraints on what is deserializable.

Markdown has a whole ecosystem of tools for handwriting Markdown. Json and many other types are not particularly friendly, although a case could be made for Toml, or maybe YAML.

## You need to work with every detail of a Markdown document as a "tree"
Use one of the many markdown libraries that expose an Abstract Syntax Tree (ast). Markpickle uses `mistune`. Not all tools that convert markdown to HTML expose an AST as part of their API and some that do, make no promises about the API being stable, such as `CommonMark`

## You need a popular data exchange format
Choose json or a type suitable for your audience.

## You need a python serializer and you trust your data
Choose pickle. It is fast, represents everything possible to serialize.

## You need to convert Markdown to HTML
Choose any markdown library, such as Mistune.

## You want to do HTML things with Markdown
Convert the markdown to HTML, then use libraries like Beautiful Soup to parse the HTML.

## You have a dictionary where the keys are HTML tags names and the values are HTML plain text.
For example, 

```python
dom = {
    "h1": "Title",
    "p": "This is my document"
}
```

And you want to convert the above to markdown or HTML, use [json2md](https://github.com/IonicaBizau/json2md)
