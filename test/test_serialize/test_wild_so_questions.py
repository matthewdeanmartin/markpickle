import markpickle


def test_lists_to_serialize():
    # CC, example source:
    # https://stackoverflow.com/questions/73880795/convert-nested-lists-from-json-string-to-md-string-using-pypandoc
    # same idea
    # https://stackoverflow.com/questions/52335498/convert-list-object-to-unordered-list-in-markdown
    data = [
        "Item A",
        "Item B",
        "Item C",
        ["Sub Item C.1", "Sub Item C.2", "Sub Item C.3"],
        "Item D",
        ["Sub Item D.1", "Sub Item D.2"],
        "Item E",
    ]
    markdown = markpickle.dumps(data)

    assert markdown == """- Item A
- Item B
- Item C
  - Sub Item C.1
  - Sub Item C.2
  - Sub Item C.3
- Item D
  - Sub Item D.1
  - Sub Item D.2
- Item E
"""


def test_ip_who_is():
    # question from https://stackoverflow.com/questions/44768989/how-to-convert-json-object-to-markdown-using-pypandoc-without-writing-to-file
    # example from https://ipwhois.io/documentation
    data = {
        "ip": "8.8.4.4",
        "success": True,
        "type": "IPv4",
        "continent": "North America",
        "continent_code": "NA",
        "country": "United States",
        "country_code": "US",
        "region": "California",
        "region_code": "CA",
        "city": "Mountain View",
        "latitude": 37.3860517,
        "longitude": -122.0838511,
        "is_eu": False,
        "postal": "94039",
        "calling_code": "1",
        "capital": "Washington D.C.",
        "borders": "CA,MX",
        "flag": {"img": "https://cdn.ipwhois.io/flags/us.svg", "emoji": "🇺🇸", "emoji_unicode": "U+1F1FA U+1F1F8"},
        "connection": {"asn": 15169, "org": "Google LLC", "isp": "Google LLC", "domain": "google.com"},
        "timezone": {
            "id": "America/Los_Angeles",
            "abbr": "PDT",
            "is_dst": True,
            "offset": -25200,
            "utc": "-07:00",
            "current_time": "2022-04-22T14:31:48-07:00",
        },
        "currency": {"name": "US Dollar", "code": "USD", "symbol": "$", "plural": "US dollars", "exchange_rate": 1},
        "security": {"anonymous": False, "proxy": False, "vpn": False, "tor": False, "hosting": False},
    }
    markdown = markpickle.dumps(data)

    # Doesn't blow up. Maybe should test with all possible patterns for subtables/nested dictionaries
    assert markdown
