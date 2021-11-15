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
            if args.config_file:
                args.config_file.close()
            self.expressions = []
            return

        file = args.config_file
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

    def clean(self, expressions):
        if len(expressions) == 0:
            return

        # Remove lines matching any expression
        for regexp in expressions:
            subs = filter(lambda sub: not sub.matches(regexp), self.subs)

        self.subs = list(subs)

    def shift(self, ms):
        for sub in self.subs:
            sub.shift(ms)
        self.subs = list(filter(lambda sub: sub.time_start >= 0, self.subs))

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
        if args.clean:
            self.clean(config.expressions)

        if args.shift:
            self.shift(args.shift)

        if args.no_html:
            self.strip_html()

        self.renumber()
        self.write_file()

    def write_file(self):
        output = open(self.file_name, 'w', encoding='utf-8')
        output.write(repr(self))
        if len(self.subs) > 0:
            output.write('\n')
        output.close()

    def __repr__(self):
        return '\n\n'.join(map(repr, self.subs))


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog='fsub',
        description='Fix, edit and clean SubRip (.srt) files.',
        add_help=True
    )

    parser.add_argument(
        '-c', '--clean',
        help='remove subtitles matching regular expressions ' +
             'listed in the config file (this is the default ' +
             'behavior if no other flag is passed)',
        action='store_true'
    )

    parser.add_argument(
        '-s', '--shift',
        help='shift all subtitles by MS milliseconds, which ' +
             'may be positive or negative',
        metavar='MS',
        action='store',
        type=int
    )

    parser.add_argument(
        '-n', '--no-html',
        help='strip HTML tags from subtitles content',
        action='store_true'
    )

    parser.add_argument(
        '-f', '--config-file',
        help='overwrite the default config file (Unix: $HOME/.config/fsubrc,' +
             r' Windows: %%APPDATA%%\fsubrc)',
        metavar='FILE',
        action='store',
        type=argparse.FileType('r')
    )

    parser.add_argument(
        'files',
        help='list of input files (they all must be SubRip files)',
        metavar='file',
        type=argparse.FileType('rb+'),
        nargs='+'
    )

    args = parser.parse_args(args)

    # Make sure --clean is the default
    if not args.shift and not args.no_html:
        args.clean = True

    # Validate options
    if not args.clean and args.config_file:
        panic('-f requires -c', 1)

    return args


def run(args):
    args = parse_args(args)
    config = ConfigFile(args)

    parsed_files = []
    for file in args.files:
        parsed_files.append(SubripFile(file))

    # TODO: join, split files

    for file in parsed_files:
        file.process(args, config)


def main():
    run(list(iter(sys.argv).next()))


if __name__ == '__main__':
    main()
