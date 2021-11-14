# fsub
`fsub` is a Python script for cleaning, editing and fixing a SubRip (.srt) file

# Installation
Through Python's pip:
```
pip install fsub
```

# Usage
```
usage: fsub [-h] [-c] [-s MS] [-n] [-f FILE] file [file ...]

Fix, edit and clean SubRip (.srt) files.

positional arguments:
  file                  list of input files (they all must be SubRip files)

optional arguments:
  -h, --help            show this help message and exit
  -c, --clean           removes subtitles matching regular expressions listed in
                        ~/.config/fsubrc (this is the default behavior if no other flag is
                        passed)
  -s MS, --shift MS     shifts all subtitles by MS milliseconds, which may be positive or
                        negative
  -n, --no-html         strips HTML tags from subtitles content
  -f FILE, --config-file FILE
                        overwrites the default config file (~/.config/fsubrc)
```

# Features
- Fixes subtitle numbering
- Converts files to UTF-8 encoding
- Validates file structure
- May remove subtitles containing lines that match any regular expression listed in the config file (by default `~/.config/fsubrc`)
- May shift the time of all subtitles
- May strip HTML
