# fsub
`fsub` is a Python script for cleaning, editing and fixing a SubRip (.srt) file

# Installation
Through Python's pip:
```
pip install fsub
```

# Usage
```
usage: fsub [-h] [-c] [-s MS] [-n] [-f F] [-j] [-r] file [file ...]

Fix, edit and clean SubRip (.srt) files.

positional arguments:
  file               list of input files (they all must be SubRip files)

optional arguments:
  -h, --help         show this help message and exit
  -c, --clean        remove subtitles matching regular expressions listed in the config file
                     (this is the default behavior if no other flag is passed)
  -s MS, --shift MS  shift all subtitles by MS milliseconds, which may be positive or negative
  -n, --no-html      strip HTML tags from subtitles content
  -f F, --config F   use F as the config file (by default, F is: on Unix:
                     $HOME/.config/fsubrc; on Windows: %APPDATA%\fsubrc)
  -j, --join         join all files into the first, shifting their time accordingly
  -r, --replace      edit files in-place (-j will delete joined files too)
```

# Testing
In the project's root directory, run all the tests with:
```
python -m unittest tests
```
Or, just the unit/integration tests:
```
python -m unittest tests.unit
python -m unittest tests.integration
```

# Features
- Fixes subtitle numbering
- Converts files to UTF-8 encoding
- Validates file structure
- May remove subtitles containing lines that match any regular expression listed in the config file (by default on Unix: `$HOME/.config/fsubrc`; on Windows: `%APPDATA%\fsubrc`)
- May shift the time of all subtitles
- May strip HTML
- May join files together
- May edit files in-place
