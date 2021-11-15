import unittest
import src.fsub.fsub as fsub
import shutil
import os
import inspect
from pathlib import Path


class TestFsub(unittest.TestCase):
    samples = Path('tests/samples')
    maxDiff = None

    def run_on(self, args, sample, ofile):
        ifile = inspect.stack()[1][3] + '.srt'

        sample = str(self.samples / sample) + '.srt'
        shutil.copy(sample, ifile)
        args.append(ifile)

        fsub.run(args)

        out = open(ifile)
        result = out.read()
        out.close()

        ofile = str(self.samples / ofile) + '.srt'
        cmp_file = open(ofile)
        cmp = cmp_file.read()
        cmp_file.close()

        self.assertEqual(result, cmp)
        os.remove(ifile)

    def test_cleaned(self):
        args = ['-f', str(self.samples / 'blacklist')]
        self.run_on(args, 'sample1', 'sample1-cleaned')

    def test_stripped(self):
        self.run_on(['-n'], 'sample1', 'sample1-stripped')

    def test_cleaned_stripped(self):
        args = ['-c', '-f', str(self.samples / 'blacklist'), '-n']
        self.run_on(args, 'sample1', 'sample1-cleaned-stripped')

    def test_cleaned_stripped_shifted_1h(self):
        args = ['-c',
                '-f', str(self.samples / 'blacklist'),
                '-n',
                '-s', '3600000']
        self.run_on(args, 'sample1', 'sample1-cleaned-stripped-shifted-1h')

    def test_shifted_minus_1h(self):
        args = ['-s', '-3600000']
        self.run_on(args, 'sample1', 'sample1-shifted-minus-1h')

    def test_shifted_minus_52s(self):
        args = ['-s', '-52000']
        self.run_on(args, 'sample1', 'sample1-shifted-minus-52s')


if __name__ == '__main__':
    unittest.main()
