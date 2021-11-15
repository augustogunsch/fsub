import unittest
import re
import io
import sys
import src.fsub.fsub as fsub


class TestTimeStamp(unittest.TestCase):
    def test_parse(self):
        # 3 h = 10800000 ms
        # 46 min = 2760000 ms
        # 13 s = 13000 ms
        # 93 ms
        # summed up: 13573093 ms
        t = fsub.TimeStamp('03:46:13,093')
        self.assertEqual(t.time, 13573093)
        self.assertEqual(t.hours, 3)
        self.assertEqual(t.minutes, 46)
        self.assertEqual(t.seconds, 13)
        self.assertEqual(t.millisecods, 93)

    @unittest.expectedFailure
    def test_missing_comma(self):
        fsub.TimeStamp('00:00:00000')

    @unittest.expectedFailure
    def test_missing_zeros(self):
        fsub.TimeStamp('0:0:00,00')

    def test_repr(self):
        time = '03:46:13,093'
        t = fsub.TimeStamp(time)
        self.assertEqual(repr(t), time)

    def test_operations(self):
        t1_str = '03:46:13,093'
        t1 = fsub.TimeStamp(t1_str)
        t2 = fsub.TimeStamp('07:39:50,920')
        res = fsub.TimeStamp('11:26:04,013')
        zero = fsub.TimeStamp('00:00:00,000')

        self.assertNotEqual(t1, t2)
        self.assertLess(t1, t2)
        self.assertGreater(t2, t1)

        t1 += t2

        self.assertEqual(t1, res)
        self.assertGreater(t1, t2)
        self.assertLess(t2, t1)

        t1 += -t2

        self.assertEqual(t1, fsub.TimeStamp(t1_str))
        self.assertLess(t1, t2)
        self.assertGreater(t2, t1)

        t1 -= t1
        t = t2.time
        t2 += t
        t2 -= t
        t2 -= t

        self.assertEqual(t1, zero)
        self.assertEqual(t2, zero)


class TestSubtitle(unittest.TestCase):
    sample_n = 10
    sample_start = '02:01:02,000'
    sample_end = '02:02:00,000'
    sample_content = \
        'This is a test subtitle, which\n' + \
        'may contain line breaks'
    sample_sub = '{}\n{} --> {}\n{}' \
        .format(sample_n, sample_start, sample_end, sample_content)
    sample_fname = 'some_file.srt'
    sample_line = 30

    def test_parse(self):
        sub = fsub.Subtitle(self.sample_sub,
                            self.sample_fname,
                            self.sample_line)

        self.assertEqual(sub.number, self.sample_n)
        self.assertEqual(repr(sub.time_start), self.sample_start)
        self.assertEqual(repr(sub.time_end), self.sample_end)
        self.assertEqual(len(sub), 4)

        for line in zip(self.sample_content.splitlines(), sub.content):
            self.assertEqual(line[0], line[1])

    def test_repr(self):
        sub = fsub.Subtitle(self.sample_sub,
                            self.sample_fname,
                            self.sample_line)
        self.assertEqual(repr(sub), self.sample_sub)

    def test_shift(self):
        sub = fsub.Subtitle(self.sample_sub,
                            self.sample_fname,
                            self.sample_line)
        start = fsub.TimeStamp(self.sample_start)
        end = fsub.TimeStamp(self.sample_end)
        # Some random amount
        shift_by = 2327291392

        sub.shift(shift_by)
        start += shift_by
        end += shift_by
        self.assertEqual(sub.time_start, start)
        self.assertEqual(sub.time_end, end)

    def test_replace(self):
        sub = fsub.Subtitle(self.sample_sub,
                            self.sample_fname,
                            self.sample_line)

        sub.replace(re.compile('dummy str not in sub'), '')

        self.assertEqual(repr(sub), self.sample_sub)

        sub.replace(re.compile('is a test'), 'is not a test')

        self.assertNotEqual(repr(sub), self.sample_sub)

    def test_matches(self):
        sub = fsub.Subtitle(self.sample_sub,
                            self.sample_fname,
                            self.sample_line)

        m1 = sub.matches(re.compile('dummy str not in sub'))

        self.assertFalse(m1)

        m2 = sub.matches(re.compile('is a test'))

        self.assertTrue(m2)

    @unittest.expectedFailure
    def test_bad_number(self):
        sub_str = """badnumber
02:01:02,000 --> 02:02:00,000
This is a test subtitle, which
may contain line breaks"""
        sys.stderr = io.StringIO()

        fsub.Subtitle(sub_str,
                      self.sample_fname,
                      self.sample_line)

        sys.stderr = sys.__stderr__

    @unittest.expectedFailure
    def test_neg_number(self):
        sub_str = """-1
02:01:02,000 --> 02:02:00,000
This is a test subtitle, which
may contain line breaks"""
        sys.stderr = io.StringIO()

        fsub.Subtitle(sub_str,
                      self.sample_fname,
                      self.sample_line)

        sys.stderr = sys.__stderr__

    @unittest.expectedFailure
    def test_bad_time_span(self):
        sub_str = """1
02:01:02,000 <-- 02:02:00,000
This is a test subtitle, which
may contain line breaks"""
        sys.stderr = io.StringIO()

        fsub.Subtitle(sub_str,
                      self.sample_fname,
                      self.sample_line)

        sys.stderr = sys.__stderr__

    @unittest.expectedFailure
    def test_inverted_time(self):
        sub_str = """1
12:01:02,000 --> 02:02:00,000
This is a test subtitle, which
may contain line breaks"""
        sys.stderr = io.StringIO()

        fsub.Subtitle(sub_str,
                      self.sample_fname,
                      self.sample_line)

        sys.stderr = sys.__stderr__


if __name__ == '__main__':
    unittest.main()
