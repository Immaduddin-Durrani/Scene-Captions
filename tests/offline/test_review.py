import copy, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'scripts'))
from generation.review import review_receipt, validate_review

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.track={'cues':[{'cue_id':'one','grid':{f'{d}-{e}':'[bell]' for d in (1,2,3) for e in (1,2,3)}},{'cue_id':'two','grid':{f'{d}-{e}':'[dog]' for d in (1,2,3) for e in (1,2,3)}}]}
        self.receipt=review_receipt(self.track,'captions','video',self.track['cues'])
    def approve(self):
        self.receipt['reviewer_id']='synthetic-test-reviewer'
        for cue in self.receipt['cues']:
            for group in ('checks','variants'):
                cue[group]={key:'approved' for key in cue[group]}
    def test_pending_receipt_is_not_an_approval(self):
        with self.assertRaises(ValueError):validate_review(self.track,'captions','video',self.receipt)
        self.receipt['reviewer_id']='synthetic-test-reviewer'
        with self.assertRaises(ValueError):validate_review(self.track,'captions','video',self.receipt)
    def test_complete_receipt_is_only_documented_review_not_automatic_installation(self):
        self.approve();self.assertEqual(validate_review(self.track,'captions','video',self.receipt)['status'],'documented-human-review-complete')
    def test_partial_receipt_and_missing_variant_are_rejected(self):
        self.approve();self.receipt['cues'].pop()
        with self.assertRaises(ValueError):validate_review(self.track,'captions','video',self.receipt)
        self.setUp();self.approve();self.receipt['cues'][0]['variants'].pop('3-3')
        with self.assertRaises(ValueError):validate_review(self.track,'captions','video',self.receipt)
    def test_changed_video_track_and_cue_invalidate_receipt(self):
        self.approve()
        with self.assertRaises(ValueError):validate_review(self.track,'captions','different-video',self.receipt)
        with self.assertRaises(ValueError):validate_review(self.track,'different-captions','video',self.receipt)
        changed=copy.deepcopy(self.track);changed['cues'][0]['grid']['1-1']='[wind]'
        with self.assertRaises(ValueError):validate_review(changed,'captions','video',self.receipt)
