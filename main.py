#!/usr/bin/env python3
import fileinput
import pydoc
import shutil
from enum import Enum
from typing import Union

from dataclasses import dataclass
from packaging import version
from packaging.version import Version, LegacyVersion

# https://www.debian.org/doc/debian-policy/ch-controlfields.html#version

SomeVersion = Union[LegacyVersion, Version]

lines = list(fileinput.input())


class UpdateType(Enum):
    EPOCH = "Epoch"
    MAJOR = "Major"
    MINOR = "Minor"
    PATCH = "Patch"
    DEBIAN = "Debian"
    OTHER = "Other"


@dataclass
class Update:
    name: str
    old_version: str
    new_version: str
    type: UpdateType


def longest_value(table, column_no):
    return max(len(row[column_no]) for row in table)


def update_type(old_version_str: str, new_version_str: str, depth=0) -> UpdateType:
    old_version = version.parse(old_version_str.replace(":", "!", 1))
    new_version = version.parse(new_version_str.replace(":", "!", 1))

    if isinstance(old_version, LegacyVersion) or isinstance(new_version, LegacyVersion):
        if not depth:
            return update_type(old_version_str.split("+")[0], new_version_str.split("+")[0], depth=depth + 1)
        if depth == 1:
            return update_type(old_version_str.split("~")[0], new_version_str.split("~")[0], depth=depth + 1)
        return UpdateType.OTHER
    if new_version.epoch != old_version.epoch:
        return UpdateType.EPOCH
    if new_version.major != old_version.major:
        return UpdateType.MAJOR
    if new_version.minor != old_version.minor:
        return UpdateType.MINOR
    if new_version.micro != old_version.micro:
        return UpdateType.PATCH
    if new_version.post != old_version.post:
        return UpdateType.DEBIAN
    if depth:
        return UpdateType.DEBIAN
    return UpdateType.OTHER


assert lines[0] == "VERSION 3\n"

updatelines = lines[lines.index('\n') + 1:]
updates = []

for line in updatelines:
    pkg_name, old_version_str, old_arch, _, comparison, new_version_str, new_arch, _, filename = line.split()
    if filename == "**CONFIGURE**":
        continue
    if old_version_str == "-" or new_version_str == "-":
        continue
    type = update_type(old_version_str, new_version_str)
    updates.append(Update(
        pkg_name,
        old_version_str,
        new_version_str,
        type
    ))

text = ""
for update in UpdateType:
    sub_updates = [u for u in updates if u.type == update]
    if not sub_updates:
        continue
    width = shutil.get_terminal_size((80, 20)).columns
    text += update.value.center(width, "-")

    for update in sub_updates:
        text += (
            f"{update.name:<{max(len(u.name) for u in sub_updates)}}"
            " "
            f"{update.old_version:<{max(len(u.old_version) for u in sub_updates)}}"
            " ➜ "
            f"{update.new_version:<{max(len(u.old_version) for u in sub_updates)}}"
            "\n"
        )

print(text)
