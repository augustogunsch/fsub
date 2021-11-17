#!/bin/python

#
#   fsub is a script for cleaning, editing and fixing a SubRip (.srt) file
#   Copyright (C) 2021  Augusto Lenz Gunsch
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
#   Contact information available in my website: https://augustogunsch.xyz
#

import sys
import argparse
import re
import chardet
import os
import copy
from pathlib import Path, PosixPath


def panic(message, code):
    print(message, file=sys.stderr)
    sys.exit(code)


class TimeStamp:
    def __init__(self, time_str):
        m = re.match(r'(\d{2,}):(\d{2}):(\d{2}),(\d{3})', time_str)
        if not m:
            raise Exception

        h, m, s, ms = map(int, m.groups())
        self.time = h * 3600000 + m * 60000 + s * 1000 + ms

    def getmilliseconds(self):
        return self.time % 1000

    def getseconds(self):
        return int((self.time % 60000) / 1000)

    def getminutes(self):
        return int((self.time / 60000) % 60)

    def gethours(self):
        return int(self.time / 3600000)

    millisecods = property(getmilliseconds)
    seconds = property(getseconds)
    minutes = property(getminutes)
    hours = property(gethours)

    def __int__(self):
        return self.time

    def __iadd__(self, other):
        self.time += int(other)
        return self

    def __neg__(self):
        new = copy.deepcopy(self)
        new.time = -new.time
        return new

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __lt__(self, other):
        return self.time < int(other)

    def __le__(self, other):
        return self.time <= int(other)

    def __eq__(self, other):
        return self.time == int(other)

    def __gt__(self, other):
        return self.time > int(other)

    def __ge__(self, other):
        return self.time >= int(other)

    def __repr__(self):
        return '%02d:%02d:%02d,%03d' % \
         (self.hours, self.minutes, self.seconds, self.millisecods)


class SectionMarker:
    def __init__(self, arg):
        try:
            self.marker = TimeStamp(arg)
        except Exception:
            try:
                self.marker = int(arg)
            except Exception:
                panic('Invalid section marker argument', 1)

    def include_after(self, other):
        if type(self.marker) is TimeStamp:
            return other.time_start >= self.marker
        return other.number >= self.marker

    def include_before(self, other):
        if type(self.marker) is TimeStamp:
            return other.time_end <= self.marker
        return other.number <= self.marker

    def __le__(self, other):
        return int(self) <= int(other)


class Subtitle:
    # Parse a single subtitle
    def __init__(self, lines, file_name, line_number):
        if type(lines) is str:
            lines = lines.splitlines()

        try:
            # This is mostly ignored, as the subtitles are renumbered later
            self.number = int(lines.pop(0))
            assert self.number > 0
        except Exception:
            panic('Invalid line number detected ({}:{})'
                  .format(file_name, line_number), 1)

        line_number += 1

        try:
            time_span = lines.pop(0).split(' --> ')
        except Exception:
            panic('Invalid time span format detected ({}:{})'
                  .format(file_name, line_number), 1)

        try:
            self.time_start = TimeStamp(time_span[0])
            self.time_end = TimeStamp(time_span[1])
        except Exception:
            panic('Invalid time stamp detected ({}:{})'
                  .format(file_name, line_number), 1)

        if self.time_start >= self.time_end:
            panic('End time must be greater than start time ({}:{})'
                  .format(file_name, line_number), 1)

        self.content = lines

    def __len__(self):
        return len(self.content) + 2

    def shift(self, ms):
        self.time_start += ms
        self.time_end += ms

    def replace(self, pattern, new_content):
        self.content = \
         list(map(lambda line: pattern.sub(new_content, line), self.content))

    def matches(self, regexp):
        for line in self.content:
            if regexp.search(line):
                return True
        return False

    def __repr__(self):
        return '{}\n{} --> {}\n{}'.format(
                self.number,
                self.time_start, self.time_end,
                '\n'.join(self.content)
        )


class ConfigFile:
    def __init__(self, args):
        # No reason to continue
        if not args.clean:
            if args.config:
                args.config.close()
            self.expressions = []
            return

        file = args.config
        # Set default config file if not specified
        if not file:
            home = Path.home()

            if type(home) is PosixPath:
                self.file_path = home / '.config' / 'fsubrc'
            else:
                self.file_path = Path(os.getenv('APPDATA')) / 'fsubrc'

            try:
                self.file_path.touch()
                file = self.file_path.open(mode='r')
            except PermissionError:
                panic('Can\'t access file {}: Permission denied'
                      .format(self.file_path), 1)
        else:
            self.file_path = Path(file.name)

        # Read expressions
        lines = file.read().strip().splitlines()
        file.close()
        self.expressions = list(map(re.compile, lines))


class SubripFile:
    def read_file(file):
        # Check extension
        if file.name[-4:] != '.srt':
            panic('File {} is not a SubRip file'.format(file.name), 1)

        # Read the input file
        contents = file.read()
        file.close()

        # Decode the file contents
        encoding = chardet.detect(contents)['encoding']
        if encoding is None:
            panic('Corrupt or empty file ({})'.format(file.name), 1)
        return contents.decode(encoding)

    # This method parses the file
    def __init__(self, file):
        self.file_name = file.name
        contents = SubripFile.read_file(file)

        # Count empty lines at the beginning
        line_number = 1
        for line in contents.splitlines():
            if len(line) == 0 or line.isspace():
                line_number += 1
            else:
                break

        # Split subtitles on empty lines
        chunks = re.split(r'(?:\r?\n){2}', contents.strip())

        # Create Subtitle objects
        self.subs = []
        for lines in chunks:
            sub = Subtitle(lines, self.file_name, line_number)
            self.subs.append(sub)
            line_number += len(sub) + 1

    def __iadd__(self, other):
        shift_time = self.subs[-1].time_end
        other.shift(shift_time)
        self.subs += other.subs
        return self

    def shift(self, ms):
        for sub in self.subs:
            sub.shift(ms)
        self.subs = [sub for sub in self.subs if sub.time_start >= 0]

    def strip_html(self):
        p = re.compile('<.+?>')
        for sub in self.subs:
            sub.replace(p, '')

    def renumber(self):
        i = 1
        for sub in self.subs:
            sub.number = i
            i += 1

    def process(self, args, config):
        html_regex = re.compile('<.+?>')
        new_subs = []
        for sub in self.subs:
            if args.begin and not args.begin.include_after(sub):
                new_subs.append(sub)
                continue

            if args.end and not args.end.include_before(sub):
                new_subs.append(sub)
                continue

            if args.clean and len(config.expressions) > 0:
                if any(sub.matches(regex) for regex in config.expressions):
                    continue

            if args.shift:
                sub.shift(args.shift)
                if sub.time_start < 0:
                    continue

            if args.no_html:
                sub.replace(html_regex, '')

            new_subs.append(sub)

        self.subs = new_subs

        self.write_file(args.replace)

    def write_file(self, in_place=False, stdout=False):
        self.renumber()

        if stdout:
            print(self)
            return

        try:
            if in_place:
                path = self.file_name
                output = open(path, 'w', encoding='utf-8')
            else:
                path = Path(self.file_name)
                path = path.with_name('out-' + path.name)
                output = path.open(mode='w', encoding='utf-8')
        except PermissionError:
            panic('Can\'t access file {}: Permission denied'
                  .format(path), 1)

        output.write(repr(self))

        if len(self.subs) > 0:
            output.write('\n')

        output.close()

    def delete(self):
        os.remove(self.file_name)
        del self

    def trunc_before(self, marker):
        self.subs = [sub for sub in self.subs if marker.include_after(sub)]

    def trunc_after(self, marker):
        self.subs = [sub for sub in self.subs if marker.include_before(sub)]

    def __repr__(self):
        return '\n\n'.join(map(repr, self.subs))


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog='fsub',
        description='Fix, edit and clean SubRip (.srt) files.',
        add_help=True
    )

    # Requires --clean
    parser.add_argument(
        '-f', '--config',
        help='use F as the config file (by default, on Unix it is: "$HOME/' +
             r'.config/fsubrc"; on Windows it is: "%%APPDATA%%\fsubrc")',
        metavar='F',
        action='store',
        type=argparse.FileType('r')
    )

    processing = parser.add_argument_group(
        'processing',
        'Flags that specify an action to be taken. Many may ' +
        'be specified.'
    )

    processing.add_argument(
        '-c', '--clean',
        help='remove subtitles matching regular expressions ' +
             'listed in the config file (this is the default ' +
             'behavior if no other flag is passed)',
        action='store_true'
    )

    processing.add_argument(
        '-s', '--shift',
        help='shift all subtitles by MS milliseconds, which ' +
             'may be positive or negative',
        metavar='MS',
        action='store',
        type=int
    )

    processing.add_argument(
        '-n', '--no-html',
        help='strip HTML tags from subtitles content',
        action='store_true'
    )

    processing.add_argument(
        '-j', '--join',
        help='join all files into the first, shifting their time accordingly',
        action='store_true'
    )

    # Requires --begin or --end, may have both
    processing.add_argument(
        '-u', '--cut-out',
        help='cut the specified section from the file(s) into new files',
        action='store_true'
    )

    redirection = parser.add_mutually_exclusive_group()
    redirection.add_argument(
        '-r', '--replace',
        help='edit files in-place (--join will delete joined files too), ' +
             'instead of the default behavior of outputing results into ' +
             'files prefixed with "out-"',
        action='store_true'
    )

    redirection.add_argument(
        '-p', '--stdout',
        help='dump results to stdout, and do not edit nor write any file',
        action='store_true'
    )

    parser.add_argument(
        'files',
        help='list of input files (they all must be SubRip files)',
        metavar='file',
        type=argparse.FileType('rb+'),
        nargs='+'
    )

    section = parser.add_argument_group(
        'sectioning',
        'Flags that specify a section to work in. They accept either ' +
        'a subtitle number or a time stamp in the SubRip format ' +
        '("<hours>:<minutes>:<seconds>,<milliseconds>", where hours, minutes' +
        ', seconds are 2-zero padded while milliseconds is 3-zero padded).' +
        ' fsub will not modify subtitles outside this range, except while ' +
        'joining the files.'
    )

    section.add_argument(
        '-b', '--begin',
        help='specify section beginning (inclusive)',
        metavar='B',
        action='store'
    )

    section.add_argument(
        '-e', '--end',
        help='specify section end (inclusive)',
        metavar='E',
        action='store'
    )

    args = parser.parse_args(args)

    # Flags that require section
    if args.cut_out:
        if not args.begin and not args.end:
            panic('You must specify a section to work with', 1)

    # Make sure --clean is the default
    if not any((args.shift, args.no_html, args.join, args.cut_out)):
        args.clean = True

    # Validate options
    if not args.clean and args.config:
        panic('-f requires -c', 1)

    if args.begin:
        args.begin = SectionMarker(args.begin)

    if args.end:
        args.end = SectionMarker(args.end)

    return args


def run(args):
    args = parse_args(args)
    config = ConfigFile(args)

    parsed_files = []
    for file in args.files:
        parsed_files.append(SubripFile(file))

    if args.cut_out:
        if args.begin:
            for file in parsed_files:
                file.trunc_before(args.begin)

        if args.end:
            for file in parsed_files:
                file.trunc_after(args.end)

    if args.join:
        first = parsed_files.pop(0)
        while True:
            try:
                file = parsed_files.pop(0)
                first += file
                file.delete()
            except IndexError:
                break
        parsed_files.append(first)

    for file in parsed_files:
        file.process(args, config)


def main():
    sys.argv.pop(0)
    run(sys.argv)


if __name__ == '__main__':
    main()
