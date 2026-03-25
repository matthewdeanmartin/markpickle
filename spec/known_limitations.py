"""
Known limitations in markpickle — reproduction scripts.

These are real bugs / open questions that don't yet have a fix.
Run directly:  uv run python spec/known_limitations.py
"""

import markpickle


def separator(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Nested dict round-trip fails with default config
#
# The serializer produces ATX headers for the top-level dict key, then
# serializes the nested dict as a Markdown *table*.  The deserializer
# correctly parses that table back — but as a list-of-dict (one row),
# not as the original nested dict.
#
# Hand-written ATX headers for nested dicts DO deserialize correctly,
# so the deserializer half works; the serializer is the problem.
# ---------------------------------------------------------------------------
separator("1. Nested dict -> ATX serialize/round-trip")

data = {"outer": {"inner1": "val1", "inner2": "val2"}}
serialized = markpickle.dumps(data)
deserialized = markpickle.loads(serialized)

print("Input:       ", data)
print("Serialized:\n", serialized)
print("Deserialized:", deserialized)
print("Match?       ", data == deserialized)  # False

# The deserializer CAN handle ATX-nested dicts when given the right markdown:
atx_md = "# outer\n\n## inner1\n\nval1\n\n## inner2\n\nval2\n"
print("\nHand-written ATX input:")
print(atx_md)
print("Deserializes to:", markpickle.loads(atx_md))  # correct


# ---------------------------------------------------------------------------
# 2. List-of-lists loses the outer container on serialize
#
# When every element of a list is itself a list, the serializer starts
# bullet points at indent level 1 (no level-0 bullet), so the outer
# container is invisible to the deserializer, which flattens everything.
#
# A *mixed* list like ["a", ["b", "c"]] works fine because the outer
# scalars anchor the structure.
# ---------------------------------------------------------------------------
separator("2. List-of-lists -- outer container lost on serialize")

data2 = [[1, 2], [3, 4]]
serialized2 = markpickle.dumps(data2)
deserialized2 = markpickle.loads(serialized2)

print("Input:       ", data2)
print("Serialized:  ", repr(serialized2))
print("Deserialized:", deserialized2)  # [1, 2, 3, 4] — flattened
print("Match?       ", data2 == deserialized2)  # False

# Mixed list works:
data2b = ["a", ["b", "c"], "d"]
s2b = markpickle.dumps(data2b)
r2b = markpickle.loads(s2b)
print("\nMixed list:  ", data2b, "->", r2b, "Match?", data2b == r2b)  # True


# ---------------------------------------------------------------------------
# 3. Multiple paragraphs with bold/italic become a tuple, not one string
#
# The TODO asks that several paragraphs (possibly containing inline
# formatting) be joined into one string.  Currently each paragraph
# becomes its own element and they're returned as a tuple.
#
# Open question: should *any* multi-paragraph block merge, or only when
# all paragraphs contain inline formatting?
# ---------------------------------------------------------------------------
separator("3. Multiple paragraphs with bold -> tuple, not one string")

md3 = "**bold start** and some text\n\nMore text after paragraph break\n"
result3 = markpickle.loads(md3)
print("Markdown input:")
print(md3)
print("Result:  ", result3)  # ('bold start  and some text', 'More text …')
print("Is tuple?", isinstance(result3, tuple))  # True — currently returns tuple

# Plain multi-paragraph (no bold) also becomes a tuple:
md3b = "First paragraph.\n\nSecond paragraph.\n"
result3b = markpickle.loads(md3b)
print("\nPlain multi-para:")
print("Result:  ", result3b)  # ('First paragraph.', 'Second paragraph.')
print("Is tuple?", isinstance(result3b, tuple))

print()
