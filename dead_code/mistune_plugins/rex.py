import re

pattern = re.compile(r"^[^\n:]*:[^\n]*$")
string = b"foo bar  : biz baz"  # \nkit cat: cot\n"
match = pattern.match(string.decode("utf-8"), 0)
print(match)
