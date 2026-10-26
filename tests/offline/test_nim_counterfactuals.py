"""No-network adversarial checks of blinded inputs and counterfactual result scoring."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('counterfactuals',ROOT/'scripts/diagnostics/nim-counterfactuals.py')
cf=importlib.util.module_from_spec(spec);spec.loader.exec_module(cf)


def response(event=None, finish='stop'):
    body={'events':[] if event is None else [event],'speech':[],'limitations':[]}
    return {'choices':[{'finish_reason':finish,'message':{'content':json.dumps(body)}}]}


class CounterfactualTests(unittest.TestCase):
    def test_report_from_another_manifest_is_not_scored(self):
        with self.assertRaisesRegex(ValueError, 'manifest'):
            cf.build_assessment({'manifest_sha256':'other','calls':[]},
                                {'manifest_sha256':'frozen'})

    def test_speech_positive_control_requires_explicit_completion(self):
        for reason in [None, 'length', 'content_filter']:
            call={'case':'c04-speech','http_status':200,'seconds':1,
                  'response':{'choices':[{'finish_reason':reason,
                    'message':{'content':'17 blue lanterns are beside the window.'}}]}}
            result=cf.build_assessment({'manifest_sha256':'frozen','calls':[call]},
                                       {'manifest_sha256':'frozen'})
            with self.subTest(reason=reason):
                self.assertEqual(result['rows'][0]['status'],'invalid-or-incomplete-output')
                self.assertNotIn('matches_expected',result['rows'][0])

    def test_known_shift_can_pass_and_unshifted_predictions_fail(self):
        protocol={'manifest_sha256':'frozen','cases':{
            'c01':{'category':'dog','source_support_s':[1,6]},
            'c02':{'category':'dog','source_support_s':[4,9]}}}
        def call(case,start):
            return {'case':case,'http_status':200,'seconds':1,'response':response(
                {'sound':'A dog barks','start_s':start,'end_s':start+.4})}
        report={'manifest_sha256':'frozen','calls':[call('c01-audio',3.2),call('c02-audio',6.2)]}
        result=cf.build_assessment(report,protocol)
        self.assertTrue(all(r['strict_category_present'] for r in result['rows']))
        self.assertTrue(all(r['known_silence_padding_respected'] for r in result['rows']))
        self.assertTrue(result['timing_shift_checks'][0]['pass'])
        report['calls'][1]=call('c02-audio',3.2)
        result=cf.build_assessment(report,protocol)
        self.assertFalse(result['timing_shift_checks'][0]['pass'])
        self.assertFalse(result['rows'][1]['known_silence_padding_respected'])

    def test_provider_failure_is_unscorable_and_silence_needs_no_events(self):
        calls=[{'case':'c01-audio','http_status':503,'seconds':1,'error':'capacity'},
               {'case':'c00-split-av','http_status':200,'seconds':1,'response':response()}]
        report={'manifest_sha256':'frozen','calls':calls}
        result=cf.build_assessment(report,{'manifest_sha256':'frozen'})
        self.assertEqual(result['rows'][0]['status'],'inconclusive-provider-or-transport')
        self.assertIsNone(result['timing_shift_checks'][0]['pass'])
        self.assertTrue(result['rows'][1]['mute_pass'])
        calls[1]['response']=response({'sound':'A tone','start_s':0,'end_s':10})
        self.assertFalse(cf.build_assessment(report,{'manifest_sha256':'frozen'})['rows'][1]['mute_pass'])

    def test_absent_time_fields_do_not_silently_become_uncertain_times(self):
        for event in [{'sound':'some sound'}, {'sound':'some sound','start_s':1},
                      {'sound':'some sound','start_s':None}, {'sound':'some sound','start_s':False,'end_s':2}]:
            with self.subTest(event=event), self.assertRaises(ValueError):
                cf.validate_result(response(event))

    def test_impossible_times_are_rejected_and_explicit_uncertainty_is_preserved(self):
        for start,end in [(-1,2),(2,2),(4,3),(0,11),(float('nan'),2),(0,float('inf'))]:
            with self.subTest(start=start,end=end), self.assertRaises(ValueError):
                cf.validate_result(response({'sound':'sound','start_s':start,'end_s':end}))
        event={'sound':'sound','start_s':None,'end_s':None}
        self.assertIsNone(cf.validate_result(response(event))['events'][0]['start_s'])

    def test_incomplete_valid_json_is_not_an_accepted_result(self):
        for reason in [None,'length','tool_calls']:
            with self.subTest(reason=reason), self.assertRaises(ValueError):
                cf.validate_result(response(finish=reason))

    def test_empty_output_is_valid_only_as_an_observation_not_proof_of_quality(self):
        self.assertEqual(cf.validate_result(response())['events'],[])
        with self.assertRaises(ValueError):
            cf.validate_result({'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]})

    def test_wrong_or_negated_categories_do_not_score_as_hits(self):
        for text in ['water flowing','no rain','not raining','wind rustles']:
            self.assertFalse(cf.category_present(text,'rain'))
        for text in ['no dog barks','without barking','a door closes']:
            self.assertFalse(cf.category_present(text,'dog'))
        self.assertTrue(cf.category_present('A dog barks','dog'))
        self.assertTrue(cf.category_present('Rainfall','rain'))

    def test_expected_labels_and_nonmedia_inputs_are_blocked(self):
        for text in ['A dog should bark','Listen for rain','seventeen blue lanterns']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                cf.assert_blind([cf.job('blind',[{'type':'text','text':text}], 'test')])
        with self.assertRaises(ValueError):
            cf.assert_blind([cf.job('blind',[{'type':'local_wav','path':'captions.srt'}], 'test')])
        cf.assert_blind([cf.job('blind',[{'type':'text','text':cf.PROMPT}], 'test')])


if __name__=='__main__':unittest.main()
