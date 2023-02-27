# def _make_bill(name, uid, identifier, session, chamber, title):
JURISDICTIONS = {
    "ak": {
        "name": "Alaska",
        "sessions": ["2017", "2018"],
        "chambers": ["lower", "upper"],
        "people": [
            {
                "name": "Amanda Adams",
                "chamber": "lower",
                "district": "1",
                "party": "Republican",
            },
            {
                "name": "Bob Birch",
                "chamber": "lower",
                "district": "2",
                "party": "Republican",
            },
            {
                "name": "Carrie Carr",
                "chamber": "lower",
                "district": "3",
                "party": "Democratic",
            },
            {
                "name": "Don Dingle",
                "chamber": "lower",
                "district": "4",
                "party": "Republican",
            },
            {
                "name": "Ellen Evil",
                "chamber": "upper",
                "district": "A",
                "party": "Independent",
                "old_positions": [
                    {
                        "chamber": "lower",
                        "district": "5",
                        "end_date": "2017-01-01",
                    },
                ],
            },
            {
                "name": "Frank Fur",
                "chamber": "upper",
                "district": "B",
                "party": "Democratic",
            },
            {
                "name": "Rhonda Retired",
                "chamber": "upper",
                "district": "B",
                "party": "Democratic",
                "end_date": "2017-01-01",
            },
        ],
        "bills": [
            {
                "uid": "c84e40e0-378b-4223-847a-420733d6b97e",
                "session": "2017",
                "identifier": "HR 1",
                "other_identifiers": [
                    "HCA 1",
                    "SB 14",
                ],
                "title": "Moose Freedom Act",
                "other_titles": [
                    "M.O.O.S.E",
                    "Moose & Reindeer Freedom Act",
                    "Moosemendment",
                ],
                "classifications": [
                    "bill",
                    "consitutional amendment",
                ],
                "abstracts": [
                    "Grants all moose eqaul rights under the law.",
                    "Ensure moose freedom.",
                ],
                "people": [
                    "Amanda Adams",
                ],
                "sponsors": [
                    {
                        "name": "Don Dingle",
                        "primary": True,
                    },
                    {
                        "name": "Carrie Carr",
                        "primary": False,
                    },
                ],
                "documents": [
                    {
                        "note": "Fiscal Note",
                        "link": "https://example.com/fn",
                    },
                    {
                        "note": "Legal Justification",
                        "link": "https://example.com/lj",
                    },
                ],
                "sources": [
                    "https://example.com/s1",
                    "https://example.com/s2",
                    "https://example.com/s3",
                ],
                "versions": [
                    {
                        "note": "First Draft",
                        "links": [
                            {
                                "link": "https://example.com/1.txt",
                                "media_type": "text/plain",
                                "searchable": {
                                    "text": "shove some long test in here with weird words; pneumonoultramicroscopicvolcanoiosis",
                                },
                            },
                            {
                                "link": "https://example.com/1.pdf",
                                "media_type": "application/pdf",
                            },
                        ],
                    },
                    {
                        "note": "Final Draft",
                        "links": [
                            {
                                "link": "https://example.com/f.txt",
                                "media_type": "text/plain",
                            },
                            {
                                "link": "https://example.com/f.pdf",
                                "media_type": "application/pdf",
                            },
                        ],
                    },
                ],
            },
            {
                "uid": "789ccce2-134d-4a23-99ef-8758030c3b64",
                "identifier": "HB 1",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "8aa3c18d-ed92-4f58-86d4-9a80125337b4",
                "identifier": "HB 2",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "192df848-6861-4585-9d4a-76acf32d2a6e",
                "identifier": "SB 1",
                "session": "2018",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "c3fd6e2b-8033-46fd-beff-54be7e0d4f50",
                "identifier": "SB 2",
                "session": "2017",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "0058eb73-f5a1-412e-965f-ced67400fa6f",
                "identifier": "HB 10",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "61d0e174-dceb-4746-b4c5-c75ee4585802",
                "identifier": "HB 10",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "c6d7811d-dcdd-4411-ac9c-e2ca8086c8ef",
                "identifier": "SB 10",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "151d3505-3579-47c6-a4c1-0ebeaed7f36b",
                "identifier": "SB 10",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "39788111-1065-4c42-bf72-a98702f22846",
                "identifier": "HB 20",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "cb88f2ff-dbec-4a98-a5b2-d15e6d0f9f1f",
                "identifier": "HB 20",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
        ],
    },
    "wy": {
        "name": "Wyoming",
        "sessions": ["2017", "2018"],
        "chambers": ["lower", "upper"],
        "people": [
            {
                "name": "Greta Gonzalez",
                "chamber": "lower",
                "district": "1",
                "party": "Democratic",
            },
            {
                "name": "Hank Horn",
                "chamber": "lower",
                "district": "1",
                "party": "Republican",
            },
        ],
        "bills": [
            {
                "uid": "b139a5cd-79b8-4427-917c-4e44541c7a1b",
                "identifier": "HB 1",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "adef9183-8209-4010-917a-bcc2a9ff7af6",
                "identifier": "HB 1",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "f7586364-c577-4b5b-9526-68511c7e526b",
                "identifier": "SB 1",
                "session": "2018",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "8abcf653-cc94-4925-839d-03bf44e2c74b",
                "identifier": "SB 1",
                "session": "2017",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "38d45355-0447-4d63-9c83-b9b3caa054dd",
                "identifier": "HB 2",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "b0200ca1-b17d-4415-9523-c46e4ad50f87",
                "identifier": "HB 2",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "fefbcfa0-ce2d-416a-8c1c-d7c2a4d3bba1",
                "identifier": "SB 2",
                "session": "2018",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "d2643466-f58f-439a-ad76-dcb53b9a9cca",
                "identifier": "SB 2",
                "session": "2017",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "6881020d-041a-4c9e-97a4-44ae0cc830cf",
                "identifier": "HB 3",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "84e1bc74-28d2-4397-9695-4a0e64c52f9b",
                "identifier": "HB 3",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "a20a1f43-1f9e-4192-9f0e-bb240473ead9",
                "identifier": "SB 3",
                "session": "2018",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "8e6fedf2-f898-4228-9fd8-e476322e96d5",
                "identifier": "SB 3",
                "session": "2017",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "28912b69-98bb-49b7-8d5b-66b10944e03e",
                "identifier": "HB 4",
                "session": "2018",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
            {
                "uid": "a3c6534b-318c-4cef-a0af-0b08732109c9",
                "identifier": "HB 4",
                "session": "2017",
                "chamber": "lower",
                "title": "A bill defines itself",
            },
        ],
    },
    "ne": {
        "name": "Nebraska",
        "chambers": ["upper"],
        "sessions": ["2017", "2018"],
        "people": [
            {
                "name": "Quincy Quip",
                "chamber": "upper",
                "district": "1",
                "party": "Nonpartisan",
            },
            {
                "name": "Wendy Wind",
                "chamber": "upper",
                "district": "2",
                "party": "Nonpartisan",
            },
        ],
    },
    "ks": {
        "name": "Kansas",
        "chambers": ["lower", "upper"],
        "sessions": ["2019", "2020"],
        "people": [
            {
                "name": "Marv Marigold",
                "chamber": "upper",
                "district": "1",
                "party": "Nonpartisan",
                },
            {
                "name": "Norm Noodle",
                "chamber": "upper",
                "district": "2",
                "party": "Nonpartisan",
                },
            {
                "name": "Oren Ombudsman",
                "chamber": "upper",
                "district": "3",
                "party": "Nonpartisan",
                },
            {
                "name": "Pat Participle",
                "chamber": "upper",
                "district": "4",
                "party": "Nonpartisan",
                },
            {
                "name": "Inara Infinity",
                "chamber": "upper",
                "district": "5",
                "party": "Nonpartisan",
                },
            {
                "name": "Kora Kornstarch",
                "chamber": "upper",
                "district": "6",
                "party": "Nonpartisan",
                },
            {
                "name": "Herby Hancock",
                "chamber": "upper",
                "district": "7",
                "party": "Nonpartisan",
                },
            {
                "name": "Jerry Journey",
                "chamber": "upper",
                "district": "8",
                "party": "Nonpartisan",
                },
            {
                "name": "Gina Galapagos",
                "chamber": "upper",
                "district": "9",
                "party": "Nonpartisan",
                },
            {
                "name": "Yeardley Smith",
                "chamber": "upper",
                "district": "10",
                "party": "Nonpartisan",
                },
        "bills": [
            {
                "uid": "69f2cb20-ee4b-4aab-ac5c-3b91790065d5",
                "identifier": "SB 19",
                "session": "2020",
                "chamber": "upper",
                "title": "A bill defines itself",
            },
            {
                "uid": "fe919978-4fb9-46a7-929d-f39c5ec9d20e",
                "identifier": "SB 20",
                "session": "2020",
                "chamber": "upper",
                "title": "A bill defines itself",
                "sponsors": [
                    {
                        "name": "Marv Marigold",
                        "primary": True,
                    },
                    {
                        "name": "Oren Ombudsman",
                        "primary": False,
                    },
                    {
                        "name": "Yeardley Smith",
                        "primary": False,
                    },
                    {
                        "name": "Norm Noodle",
                        "primary": False,
                    },
                    {
                        "name": "Gina Galapagos",
                        "primary": False,
                    },
                    {
                        "name": "Jerry Journey",
                        "primary": False,
                    },
                    {
                        "name": "Pat Participle",
                        "primary": False,
                    },
                    {
                        "name": "Inara Infinity",
                        "primary": False,
                    },
                    {
                        "name": "Kora Kornstarch",
                        "primary": False,
                    },
                    {
                        "name": "Herby Hancock",
                        "primary": False,
                    },
                ],
                "documents": [
                    {
                        "note": "Fiscal Note",
                        "link": "https://example.com/fn",
                    },
                    {
                        "note": "Legal Justification #2",
                        "link": "https://example.com/lj2",
                    },
                    {
                        "note": "Legal Justification #3",
                        "link": "https://example.com/lj3",
                    },
                    {
                        "note": "Legal Justification #4",
                        "link": "https://example.com/lj4",
                    },
                    {
                        "note": "Legal Justification #5",
                        "link": "https://example.com/lj5",
                    },
                    {
                        "note": "Legal Justification #6",
                        "link": "https://example.com/lj6",
                    },
                    {
                        "note": "Legal Justification #7",
                        "link": "https://example.com/lj7",
                    },
                    {
                        "note": "Legal Justification #8",
                        "link": "https://example.com/lj8",
                    },
                    {
                        "note": "Legal Justification #9",
                        "link": "https://example.com/lj9",
                    },
                    {
                        "note": "Legal Justification #10",
                        "link": "https://example.com/lj10",
                    },
                ],
                "versions": [
                    {
                        "note": "First Draft",
                        "links": [
                            {
                                "link": "https://example.com/1.txt",
                                "media_type": "text/plain",
                            },
                        ],
                    },
                    {
                        "note": "Second Draft",
                        "links": [
                            {
                                "link": "https://example.com/2.txt",
                                "media_type": "text/plain",
                            },
                        ],
                    },
                    {
                        "note": "Third Draft",
                        "links": [
                            {
                                "link": "https://example.com/3.txt",
                                "media_type": "text/plain",
                            },
                        ],
                    },
                    {
                        "note": "Final Draft",
                        "links": [
                            {
                                "link": "https://example.com/f.txt",
                                "media_type": "text/plain",
                            },
                        ],
                    },
                ],
            },
        ],
    },
}
