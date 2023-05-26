# What if you could `import` a `markdown` file?

It would be a way to write instantly documented code.

One draw back is that you need to write a .pyi file to get code completion in an IDE.

```python
def some_function(args):
    """This is a function that does something."""
    return "Hello World"
```

Here is another function

```python
def another_function(a:int, b:int)->int:
    """Add them up."""
    return a + b
```
