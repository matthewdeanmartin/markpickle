1. All about the bug fixes.

1. html-style markdown to dict (where everything is a dict, with {"h1": "title"})

1. Fix deps
   3\. Make tabulate optional (own implementation for table)
   4\. Make pillow optional
   5\. Make markdown formatter optional
   6\. Mistune is a hard dep (but can't move forward!)

1. tkinter GUI

   1. Format
   1. Convert to Markdown
   1. Markdown to Python
   1. View config
   1. Validate (can it safely convert)
   1. doctor

1. Commands
   4\. `markpickle` cli command
   5\. Doctor (show what optional 3rd party libs are available and other diagnostic info)
   5\. convert .md .py
   6\. validate (can it be safely converted)
   7\. config=config.toml

## Maybe someday, but not today

More deps
7\. Optional glom
8\. Optional cerberus
More commands
4\. Validate (python) with cerberus
5\. Query (python) with glom
