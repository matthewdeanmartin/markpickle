import mistune

print(mistune.__version__)

md = mistune.create_markdown(renderer="ast")
result = md("""# cat
## dog
abc
## rabbit
123
""")
print(result)
print(type(result))
assert result
