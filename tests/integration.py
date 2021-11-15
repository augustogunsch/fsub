import unittest
import src.fsub.fsub as fsub
import shutil
import os
import inspect
from pathlib import Path


class TestFsub(unittest.TestCase):
    samples = Path('tests/samples')

    def run_on(self, args, samples, ofiles):
        caller = inspect.stack()[1][3]
        ifiles = []

        samples = map(lambda s: str(self.samples / s) + '.srt', samples)
        i = 1
        for sample in samples:
            ifile = str(i) + '.' + caller + '.srt'
            shutil.copy(sample, ifile)
            args.append(ifile)
            ifiles.append(ifile)
            i += 1

        fsub.run(args)

        limit = len(ofiles)
        for i, ifile in enumerate(ifiles):
            if i < limit:
                out = open(ifile)
                result = out.read()
                out.close()

                ofile = str(self.samples / ofiles[i]) + '.srt'
                cmp_file = open(ofile)
                cmp = cmp_file.read()
                cmp_file.close()

                self.assertEqual(result, cmp)
            os.remove(ifile)

    def test_cleaned(self):
        args = ['-f', str(self.samples / 'blacklist')]
        self.run_on(args, ['sample1'], ['sample1-cleaned'])

    def test_stripped(self):
        self.run_on(['-n'], ['sample1'], ['sample1-stripped'])

    def test_cleaned_stripped(self):
        args = ['-c', '-f', str(self.samples / 'blacklist'), '-n']
        self.run_on(args, ['sample1'], ['sample1-cleaned-stripped'])

    def test_cleaned_stripped_shifted_1h(self):
        args = ['-c',
                '-f', str(self.samples / 'blacklist'),
                '-n',
                '-s', '3600000']
        self.run_on(args, ['sample1'], ['sample1-cleaned-stripped-shifted-1h'])

    def test_shifted_minus_1h(self):
        args = ['-s', '-3600000']
        self.run_on(args, ['sample1'], ['sample1-shifted-minus-1h'])

    def test_shifted_minus_52s(self):
        args = ['-s', '-52000']
        self.run_on(args, ['sample1'], ['sample1-shifted-minus-52s'])

    def test_joined(self):
        args = ['-j']
        self.run_on(args, ['sample1', 'sample2', 'sample3'],
                          ['sample1-sample2-sample3-joined'])


if __name__ == '__main__':
    unittest.main()
