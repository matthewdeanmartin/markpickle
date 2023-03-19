# Data types Markdown supports

**String**. Can you infer types? Probably not.

**List**. And lists can hold String, List, Dict\[int, str\],

```markdown
 - Cat
 - Dog
 - Rabbit
```

**Dict\[int, str | list | dict\[int, str\]\]**. Also known as ordered lists. Can hold most types.

```markdown
1. Cat
2. Dog
3. Rabbit
```

**Dict\[int, str\]**. Also known as ordered lists.

**Dict\[str, str\]**. Via headers

```markdown
# Things
## Animals
 - Cat
 - Dog
 - Rabbit
## Plants
 - Tree
 - Potato
 - Radish
```

**Dict\[int, dict\[str, str\]\]** Dictionary of numeric keys and value that are dictionaries.

```markdown
# dict of lists of strings

1. | author | title    | pub_date |
   | ------ | -------- | -------- |
   | john   | the book | 1922     |

2. | author | title    | pub_date |
   | ------ | -------- | -------- |
   | john   | the book | 1922     |
```
