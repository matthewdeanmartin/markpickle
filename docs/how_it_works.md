# How it works

## Documents

Documents are divided by triple dashes. A document can serialize one python object.

## Scalars
Numbers looks the same as strings.

Blanks look the same as whitespace strings and Null/None types.

Data URLS in images are bytes.

## Dictionaries
You get one "ATX Header" style dictionary.

Each header section, e.g. # start a key. The document until the next single # is the value.

## Lists
Lists nest but you can't put an ATX Header dictionary inside a list.

