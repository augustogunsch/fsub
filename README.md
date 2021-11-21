# fsub
`fsub` is a Python script for cleaning, editing and fixing a SubRip (.srt) file

# Installation
Through Python's pip:
```
pip install fsub
```

# Usage
```
usage: fsub [-h] [-f F] [-c] [-s MS] [-n] [-j] [-u] [-r | -p] [-b B] [-e E] file [file ...]

Fix, edit and clean SubRip (.srt) files.

positional arguments:
  file               list of input files (they all must be SubRip files)

optional arguments:
  -h, --help         show this help message and exit
  -f F, --config F   use F as the config file (by default, on Unix it is:
                     "$HOME/.config/fsubrc"; on Windows it is: "%APPDATA%\fsubrc")
  -r, --replace      edit files in-place (--join will delete joined files too), instead of the
                     default behavior of outputing results into files prefixed with "out-"
  -p, --stdout       dump results to stdout, and do not edit nor write any file

processing:
  Flags that specify an action to be taken. Many may be specified.

  -c, --clean        remove subtitles matching regular expressions listed in the config file
                     (this is the default behavior if no other flag is passed)
  -s MS, --shift MS  shift all subtitles by MS milliseconds, which may be positive or negative
  -n, --no-html      strip HTML tags from subtitles content
  -j, --join         join all files into the first, shifting their time accordingly
  -u, --cut-out      cut the specified section from the file(s) into new files

sectioning:
  Flags that specify a section to work in. They accept either a subtitle number or a time
  stamp in the SubRip format ("<hours>:<minutes>:<seconds>,<milliseconds>", where hours,
  minutes, seconds are 2-zero padded while milliseconds is 3-zero padded). fsub will not
  modify subtitles outside this range, except while joining the files.

  -b B, --begin B    specify section beginning (inclusive)
  -e E, --end E      specify section end (inclusive)
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

# Scripted API
An example of calling the program from Python:
```
import fsub

fsub.run('-c', 'test.srt')
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
- May cut sections out
