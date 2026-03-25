1. All about the bug fixes.
2. html-style markdown to dict (where everything is a dict, with {"h1": "title"})
2. Fix deps
   3. Make tabulate optional (own implementation for table)
   4. Make pillow optional
   5. Make markdown formatter optional
   6. Mistune is a hard dep (but can't move forward!)
   
2. tkinter GUI
   1. Format
   2. Convert to Markdown
   3. Markdown to Python
   4. View config
   5. Validate (can it safely convert)
   6. doctor
3. Commands
   4. `markpickle` cli command
   5. Doctor (show what optional 3rd party libs are available and other diagnostic info)
   5. convert .md .py
   6. validate (can it be safely converted)
   7. config=config.toml 

## Maybe someday, but not today
More deps
    7. Optional glom
   8. Optional cerberus
More commands
   4. Validate (python) with cerberus
   5. Query (python) with glom
   