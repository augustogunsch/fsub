# fsub
`fsub` is a Python script for cleaning, editing and fixing a SubRip (.srt) file

# Usage
```
usage: fsub [-h] [-c] [-s MS] [-n] file [file ...]

Fix, edit and clean SubRip (.srt) files.

positional arguments:
  file               list of input files (they all must be SubRip files)

optional arguments:
  -h, --help         show this help message and exit
  -c, --clean        removes subtitles matching regular expressions listed in ~/.config/fsubrc
                     (this is the default behavior if no other flag is passed)
  -s MS, --shift MS  shifts all subtitles by MS milliseconds, which may be positive or
                     negative
  -n, --no-html      strips HTML tags from subtitles content
```

# Features
- Fixes subtitle numbering
- Converts files to UTF-8 encoding
- Validates file structure
- May remove subtitles containing lines that match any regular expression listed in `~/.config/fsubrc`
- May shift the time of all subtitles
- May strip HTML
