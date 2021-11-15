# fsub
`fsub` is a Python script for cleaning, editing and fixing a SubRip (.srt) file

# Installation
Through Python's pip:
```
pip install fsub
```

# Usage
```
usage: fsub [-h] [-c] [-s MS] [-n] [-f FILE] [-j] file [file ...]

Fix, edit and clean SubRip (.srt) files.

positional arguments:
  file                  list of input files (they all must be SubRip files)

optional arguments:
  -h, --help            show this help message and exit
  -c, --clean           remove subtitles matching regular expressions listed in the config
                        file (this is the default behavior if no other flag is passed)
  -s MS, --shift MS     shift all subtitles by MS milliseconds, which may be positive or
                        negative
  -n, --no-html         strip HTML tags from subtitles content
  -f FILE, --config-file FILE
                        overwrite the default config file (Unix: $HOME/.config/fsubrc,
                        Windows: %APPDATA%\fsubrc)
  -j, --join            join all files into the first, shifting their time accordingly (this
                        will delete files)
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
