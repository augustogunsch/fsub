import unittest
import src.fsub.fsub as fsub
import shutil
import os
import inspect
from pathlib import Path


class TestFsub(unittest.TestCase):
    samples = Path('tests/samples')

    def run_on(self, args, samples, expect_out_files, replace=False):
        caller = inspect.stack()[1][3]
        cloned_samples = []

        samples = map(lambda s: str(self.samples / s) + '.srt', samples)
        i = 1
        for sample in samples:
            cloned_sample = str(i) + '.' + caller + '.srt'
            shutil.copy(sample, cloned_sample)
            args.append(cloned_sample)
            cloned_samples.append(cloned_sample)
            i += 1

        fsub.run(args)

        limit = len(expect_out_files)
        for i, cloned_sample in enumerate(cloned_samples):
            if i < limit:
                if not replace:
                    os.remove(cloned_sample)
                    cloned_sample = 'out-' + cloned_sample
                out = open(cloned_sample)
                result = out.read()
                out.close()

                expect_out_file = str(self.samples/expect_out_files[i])+'.srt'
                expect_out_file = open(expect_out_file)
                expect_out = expect_out_file.read()
                expect_out_file.close()

                self.assertEqual(result, expect_out)
            try:
                os.remove(cloned_sample)
            except FileNotFoundError:
                pass

    def test_cleaned(self):
        args = ['-f', str(self.samples / 'blacklist')]
        self.run_on(args, ['sample1'], ['sample1-cleaned'])

    def test_cleaned_begin(self):
        args = ['-f', str(self.samples / 'blacklist'), '-b', '3']
        self.run_on(args, ['sample1'], ['sample1-cleaned-begin'])

    def test_stripped(self):
        self.run_on(['-n'], ['sample1'], ['sample1-stripped'])

    def test_stripped_end(self):
        args = ['-n', '-e', '00:00:55,500']
        self.run_on(args, ['sample1'], ['sample1-stripped-end'])

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

    def test_shifted_minus_1h_begin(self):
        args = ['-s', '-3600000', '-b', '00:00:53,500']
        self.run_on(args, ['sample1'], ['sample1-shifted-minus-1h-begin'])

    def test_joined(self):
        args = ['-j']
        self.run_on(args, ['sample1', 'sample2', 'sample3'],
                          ['sample1-sample2-sample3-joined'])

    def test_cut_begin(self):
        args = ['-b', '2', '-u']
        self.run_on(args, ['sample1'], ['sample1-cut-out-begin'])

    def test_cut_end(self):
        args = ['-e', '1', '-u']
        self.run_on(args, ['sample1'], ['sample1-cut-out-end'])

    def test_cut_begin_end(self):
        args = ['-b', '2', '-e', '4', '-u']
        self.run_on(args, ['sample1'], ['sample1-cut-out-begin-end'])

    def test_cut_end_joined(self):
        args = ['-e', '1', '-u', '-j']
        self.run_on(args, ['sample1', 'sample3'],
                          ['sample1-sample3-cut-out-end-joined'])


if __name__ == '__main__':
    unittest.main()
