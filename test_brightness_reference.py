import unittest
from brightness_reference import load_brightness_audit
class BrightnessReferenceTests(unittest.TestCase):
    def test_data_loads(self):
        rules,audit=load_brightness_audit()
        self.assertGreater(audit['source_entries'],100)
        self.assertEqual(audit['verified_entries'],sum(map(len,rules.values())))
        self.assertIn('紫微',rules)
        self.assertIn('子',rules['紫微'])
    def test_not_claim_independent_verification(self):
        _,audit=load_brightness_audit()
        self.assertIn('not_independently_verified',audit['status'])
if __name__=='__main__':unittest.main()
