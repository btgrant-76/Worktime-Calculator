from pytest import mark

from work_time_calculator import (
    _group_events_by_date,
    _clean,
    _group_times_by_tag,
    _total_times,
    _count_time,
    _generate_subtotal_output_lines,
    _generate_total_line,
    _filter_unmatched_tags,
)

FILE_LINES = [
    "😴 .5\n",
    "Scheduled: Mar 8, 2021 at 8:15 AM to 8:45 AM\n",
    "\n",
    "👨🏻‍🏫 1.75\n",
    "Scheduled: Mar 8, 2021 at 8:45 AM to 10:30 AM\n",
    "\n",
    "👨🏻‍💻 .75\n",
    "Scheduled: Mar 9, 2021 at 4:45 PM to 5:30 PM\n",
    "\n",
    "👨🏻‍🏫 (1)\n",
    "Scheduled: Mar 10, 2021 at 6:00 AM to 7:00 AM\n",
    "\n",
    "😴 1.25\n",
    "Scheduled: Mar 10, 2021 at 7:30 AM to 8:45 AM\n",
]

FILE_LINES_WITH_TIMEZONE = [
    "😴 .5\n",
    "Scheduled: Mar 8, 2021 at 8:15 AM to 8:45 AM, CDT\n",
    "\n",
    "👨🏻‍🏫 1.75\n",
    "Scheduled: Mar 8, 2021 at 8:45 AM to 10:30 AM, CDT\n",
    "\n",
    "👨🏻‍💻 .75\n",
    "Scheduled: Mar 9, 2021 at 4:45 PM to 5:30 PM, CDT\n",
    "\n",
    "👨🏻‍🏫 (1)\n",
    "Scheduled: Mar 10, 2021 at 6:00 AM to 7:00 AM, CDT\n",
    "\n",
    "😴 1.25\n",
    "Scheduled: Mar 10, 2021 at 7:30 AM to 8:45 AM, CDT\n",
]

ICAL_BUDDY_FILE_LINES = [
    "😴 .5\n",
    "    Mar 8, 2021 at 8:15 AM - 8:45 AM\n",
    "\n",
    "👨🏻‍🏫 1.75\n",
    "    Mar 8, 2021 at 8:45 AM - 10:30 AM\n",
    "\n",
    "👨🏻‍💻 .75\n",
    "    Mar 9, 2021 at 4:45 PM - 5:30 PM\n",
    "\n",
    "👨🏻‍🏫 (1)\n",
    "    Mar 10, 2021 at 6:00 AM - 7:00 AM\n",
    "\n",
    "😴 1.25\n",
    "    Mar 10, 2021 at 7:30 AM - 8:45 AM\n",
]

CLEANED_LINES = [
    "😴",
    "Mar 8, 2021 at 8:15 AM to 8:45 AM",
    "👨🏻‍🏫",
    "Mar 8, 2021 at 8:45 AM to 10:30 AM",
    "👨🏻‍💻",
    "Mar 9, 2021 at 4:45 PM to 5:30 PM",
    "👨🏻‍🏫",
    "Mar 10, 2021 at 6:00 AM to 7:00 AM",
    "😴",
    "Mar 10, 2021 at 7:30 AM to 8:45 AM",
]


@mark.parametrize(
    "lines, cleaned_lines",
    [
        (FILE_LINES, CLEANED_LINES),
        (FILE_LINES_WITH_TIMEZONE, CLEANED_LINES),
        (ICAL_BUDDY_FILE_LINES, CLEANED_LINES),
    ],
)
def test_clean(lines, cleaned_lines):
    cleaned = _clean(lines)
    assert cleaned == cleaned_lines


def test_grouping():
    grouped_events = _group_events_by_date(CLEANED_LINES)
    assert grouped_events == {
        "Mar 8, 2021": [
            ("😴", "8:15 AM to 8:45 AM"),
            ("👨🏻‍🏫", "8:45 AM to 10:30 AM"),
        ],
        "Mar 9, 2021": [
            ("👨🏻‍💻", "4:45 PM to 5:30 PM"),
        ],
        "Mar 10, 2021": [("👨🏻‍🏫", "6:00 AM to 7:00 AM"), ("😴", "7:30 AM to 8:45 AM")],
    }


def test_tag_grouping():
    grouped_events = {
        "Mar 8, 2021": [
            ("😴", "8:15 AM to 8:45 AM"),
            ("👨🏻‍🏫", "8:45 AM to 10:30 AM"),
            ("👨🏻‍🏫", "1:00 PM to 3:30 PM"),
        ],
        "Mar 9, 2021": [
            ("👨🏻‍💻", "4:45 PM to 5:30 PM"),
        ],
        "Mar 10, 2021": [
            ("👨🏻‍🏫", "6:00 AM to 7:00 AM"),
            ("😴", "7:30 AM to 8:45 AM"),
            ("👨🏻‍🏫", "9:00 AM to 10:00 AM"),
            ("😴", "10:30 AM to 12:00 PM"),
        ],
    }

    times_grouped_by_tag = _group_times_by_tag(grouped_events)
    assert times_grouped_by_tag == {
        "Mar 8, 2021": {
            "😴": ["8:15 AM to 8:45 AM"],
            "👨🏻‍🏫": ["8:45 AM to 10:30 AM", "1:00 PM to 3:30 PM"],
        },
        "Mar 9, 2021": {"👨🏻‍💻": ["4:45 PM to 5:30 PM"]},
        "Mar 10, 2021": {
            "👨🏻‍🏫": ["6:00 AM to 7:00 AM", "9:00 AM to 10:00 AM"],
            "😴": ["7:30 AM to 8:45 AM", "10:30 AM to 12:00 PM"],
        },
    }


def test_filter_unmatched_tags():
    inputs = {
        "Mar 8, 2021": {
            "invalid": ["4:00 PM to 4:45 PM"],
            "😴": ["8:15 AM to 8:45 AM"],
            "👨🏻‍🏫": ["8:45 AM to 10:30 AM", "1:00 PM to 3:30 PM"],
        },
        "Mar 9, 2021": {
            "👨🏻‍💻": ["4:45 PM to 5:30 PM"],
            "also invalid": ["4:00 PM to 4:45 PM"],
        },
        "Mar 10, 2021": {
            "👨🏻‍🏫": ["6:00 AM to 7:00 AM", "9:00 AM to 10:00 AM"],
            "invalid, too": ["4:00 PM to 4:45 PM"],
            "😴": ["7:30 AM to 8:45 AM", "10:30 AM to 12:00 PM"],
        },
    }

    assert _filter_unmatched_tags(inputs) == {
        "Mar 8, 2021": {
            "😴": ["8:15 AM to 8:45 AM"],
            "👨🏻‍🏫": ["8:45 AM to 10:30 AM", "1:00 PM to 3:30 PM"],
        },
        "Mar 9, 2021": {
            "👨🏻‍💻": ["4:45 PM to 5:30 PM"],
        },
        "Mar 10, 2021": {
            "👨🏻‍🏫": ["6:00 AM to 7:00 AM", "9:00 AM to 10:00 AM"],
            "😴": ["7:30 AM to 8:45 AM", "10:30 AM to 12:00 PM"],
        },
    }


def test_total_times():
    totaled = _total_times(
        {
            "Mar 8, 2021": {
                "😴": ["8:15 AM to 8:45 AM"],
                "👨🏻‍🏫": ["8:45 AM to 10:30 AM", "1:00 PM to 3:30 PM"],
            },
            "Mar 9, 2021": {"👨🏻‍💻": ["4:45 PM to 5:30 PM"]},
            "Mar 10, 2021": {
                "👨🏻‍🏫": ["6:00 AM to 7:00 AM", "9:00 AM to 10:00 AM"],
                "😴": ["7:30 AM to 8:45 AM", "10:30 AM to 12:00 PM"],
            },
        }
    )

    assert totaled == {
        "Mar 8, 2021": [("😴", 0.5), ("👨🏻‍🏫", 4.25)],
        "Mar 9, 2021": [("👨🏻‍💻", 0.75)],
        "Mar 10, 2021": [("👨🏻‍🏫", 2.0), ("😴", 2.75)],
    }


@mark.parametrize(
    "input_time, minutes",
    [
        ("6:00 AM to 7:00 AM", 1.0),
        ("6:00 AM to 6:30 AM", 0.5),
        ("6:00 PM to 7:00 PM", 1.0),
        ("6:00 PM to 6:30 PM", 0.5),
        ("10:30 AM to 12:00 PM", 1.5),
    ],
)
def test_count_time(input_time, minutes):
    assert _count_time(input_time) == minutes


def test_generate_file_lines():
    totaled = {
        "Mar 8, 2021": [("😴", 0.5), ("👨🏻‍🏫", 4.25)],
        "Mar 9, 2021": [("👨🏻‍💻", 0.75)],
        "Mar 10, 2021": [("👨🏻‍🏫", 2.0), ("😴", 2.75)],
    }

    assert _generate_subtotal_output_lines(totaled) == [
        "Mar 8, 2021: 👨🏻‍💻: 0 👨🏻‍🏫: 4.25 😴: 0.5",
        "Mar 9, 2021: 👨🏻‍💻: 0.75 👨🏻‍🏫: 0 😴: 0",
        "Mar 10, 2021: 👨🏻‍💻: 0 👨🏻‍🏫: 2.0 😴: 2.75",
    ]


def test_generate_total_line():
    totaled = {
        "Mar 8, 2021": [("😴", 0.5), ("👨🏻‍🏫", 4.25)],
        "Mar 9, 2021": [("👨🏻‍💻", 0.75)],
        "Mar 10, 2021": [("👨🏻‍🏫", 2.0), ("😴", 2.75)],
    }

    assert _generate_total_line(totaled) == "👨🏻‍💻: 0.75/16 👨🏻‍🏫: 6.25/16 😴: 3.25/8"


def test_generate_total_line_default_to_zero():
    totaled = {"Mar 8, 2021": [], "Mar 9, 2021": [], "Mar 10, 2021": []}

    assert _generate_total_line(totaled) == "👨🏻‍💻: 0/16 👨🏻‍🏫: 0/16 😴: 0/8"
