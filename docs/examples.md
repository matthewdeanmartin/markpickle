# Examples

## Single Documents

### scalar

```python
6
```

```markdown
6
```

Roundtripable? Yes

### binary

```python
b'hello world'
```

```markdown
![bytes](data:application/octet-stream;base64,aGVsbG8gd29ybGQ=)
```

Roundtripable? Yes

### list of scalars

```python
[1, 2, 3]
```

```markdown
- 1
- 2
- 3
```

Roundtripable? Yes

### list of binary

```python
[b'hello world', b'hello universe']
```

```markdown
- ![bytes](data:application/octet-stream;base64,aGVsbG8gd29ybGQ=)
- ![bytes](data:application/octet-stream;base64,aGVsbG8gdW5pdmVyc2U=)
```

Roundtripable? No

### list of dictionaries

```python
[{'animal': 'cat', 'name': 'Frisky'}, {'animal': 'dog', 'name': 'Fido'}]
```

```markdown
| animal | name   |
| ------ | ------ |
| cat    | Frisky |
| dog    | Fido   |
```

Roundtripable? No

### dictionaries of strings

```python
{'animal': 'cat', 'name': 'Frisky'}
```

```markdown
# animal
cat
# name
Frisky
```

Roundtripable? Yes

### dictionaries of binary

```python
{'animal': b'hello world', 'name': b'hello universe'}
```

```markdown
# animal
![bytes](data:application/octet-stream;base64,aGVsbG8gd29ybGQ=)
# name
![bytes](data:application/octet-stream;base64,aGVsbG8gdW5pdmVyc2U=)
```

Roundtripable? No

### dictionary of lists

```python
{'ages': [24, 59, 45], 'countries': ['US', 'Canada', 'Iceland']}
```

```markdown
- ages
 - 24
 - 59
 - 45
- countries
 - US
 - Canada
 - Iceland
```

Roundtripable? No

### dictionary of dictionaries

```python
{'Best Cat': {'animal': 'cat', 'name': 'Frisky'}, 'Best Dog': {'animal': 'dog', 'name': 'Fido'}}
```

```markdown
# Best Cat

 | animal | name   |
 | ------ | ------ |
 | cat    | Frisky |

# Best Dog

 | animal | name |
 | ------ | ---- |
 | dog    | Fido |

```

Roundtripable? No

## Examples of multiple document in one file

### two scalar documents

```python
['abc', 123]
```

```markdown
abc
---
123
```

### two dictionary documents

```python
[{'cat': 'Frisky'}, {'dog': 'Fido'}]
```

```markdown
# cat
Frisky
---
# dog
Fido
```
