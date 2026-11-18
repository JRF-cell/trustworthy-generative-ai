"""Contract, actual-data regression and routing-policy checks; no network."""
import unittest
from types import SimpleNamespace
from td2_common import HERE, vote, load_module, PANEL3, PANEL5, proposals, load_cells
from build_references import read_csv

router = load_module('td2_router_tests', HERE / 'atelier-routage.py')


def panel(values):
    return [SimpleNamespace(provider='test', model_requested=str(i), value=v,
                            verdict='executed' if v is not None else 'error')
            for i,v in enumerate(values)]


class VoteTests(unittest.TestCase):
    def test_zero_is_a_vote_and_reference_not_an_input(self):
        self.assertEqual(vote(panel([0,0,100]),2)['value'],0)

    def test_unavailable_members_keep_denominator(self):
        self.assertFalse(vote(panel([7,None,None]),2)['consensus'])
        self.assertFalse(vote(panel([7,7,None,None,None]),3)['consensus'])

    def test_error_with_value_does_not_vote(self):
        rows=panel([5,5,6]); rows[1].verdict='error'
        self.assertFalse(vote(rows,2)['consensus'])

    def test_no_votes(self):
        self.assertEqual(vote(panel([None]*3),2),dict(consensus=False,value=None,votes=0,models=[]))

    def test_strict_threshold(self):
        for values,k in [([],1),([1,1,1],1),([1,1,1],4),([1,1,1],2.0),([1],True),([1]*4,2)]:
            with self.subTest(values=values,k=k),self.assertRaises(ValueError):vote(panel(values),k)

    def test_trailing_duplicate_is_rejected_even_after_consensus(self):
        rows=panel([5,5,5]); rows[2].model_requested='0'
        with self.assertRaises(ValueError):vote(rows,2)

    def test_same_provider_distinct_models_allowed(self):
        result=vote(panel([3,3,3,4,4]),3)
        self.assertEqual((result['value'],result['votes'],len(result['models'])),(3,3,3))

    def test_noninteger_rejected(self):
        for value in ['3',3.0,True]:
            with self.subTest(value=value),self.assertRaises(ValueError):vote(panel([value,3,3]),2)

    def test_actual_cases(self):
        refs={r['case_id']:int(r['revenue_cents']) for r in read_csv(HERE/'reference-td1.csv')}
        cells=load_cells(HERE/'traces-td1.csv','real',refs)
        self.assertEqual(len(cells),100)
        for case in ['C02','C08']:
            self.assertEqual(vote(proposals(cells,case,PANEL3),2)['value'],refs[case])
            self.assertFalse(vote(proposals(cells,case,PANEL5),3)['consensus'])
        for case in ['C17','C19']:
            self.assertFalse(vote(proposals(cells,case,PANEL3),2)['consensus'])
            self.assertEqual(vote(proposals(cells,case,PANEL5),3)['value'],refs[case])


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.resources=router.measured_resources()
        self.request=dict(family='F1',difficulty=1,use='internal',can_wait=True,deadline_minutes=120,budget=.30)

    def test_free_perfect_internal(self):
        d=router.choose(self.request,self.resources)
        self.assertEqual((d['action'],d['checks']),('run','none'))
        self.assertIn('C01',d['reason']); self.assertIn('6/6',d['reason'])

    def test_customer_and_payout_require_reference(self):
        for use in ['customer','payout']:
            self.assertIn('reference',router.choose(dict(self.request,use=use),self.resources)['checks'])

    def test_imperfect_model_cannot_skip_check(self):
        qwen=[r for r in self.resources if r['model']=='qwen/qwen3.8-27b']
        d=router.choose(self.request,qwen)
        self.assertEqual((d['action'],d['checks']),('run','reference'))
        self.assertIn('5/6',d['reason'])

    def test_incomplete_or_zero_success_ineligible(self):
        empty=[dict(r,evidence={}) for r in self.resources]
        self.assertEqual(router.choose(self.request,empty)['action'],'abstain')
        cohere=[r for r in self.resources if 'cohere' in r['id']]
        self.assertEqual(router.choose(dict(self.request,family='F2'),cohere)['action'],'abstain')

    def test_defer_and_deadline(self):
        exhausted=[dict(r,available=False,reset_minutes=60) for r in self.resources]
        self.assertEqual(router.choose(self.request,exhausted)['action'],'defer')
        for request in [dict(self.request,can_wait=False),dict(self.request,deadline_minutes=59)]:
            self.assertEqual(router.choose(request,exhausted)['action'],'abstain')

    def test_paid_budget(self):
        paid=[dict(self.resources[0],cash=.30,allocation=.30,access='tokens')]
        self.assertEqual(router.choose(self.request,paid)['action'],'run')
        self.assertEqual(router.choose(dict(self.request,budget=.29),paid)['action'],'abstain')

    def test_subscription_priority_reversal(self):
        free=dict(self.resources[0],available=False,reset_minutes=60)
        subscription=dict(self.resources[0],id='synthetic-subscription',allocation=.04,access='subscription')
        self.assertEqual(router.choose(self.request,[free,subscription])['resource'],'synthetic-subscription')
        d=router.choose(dict(self.request,preserve_subscription=True),[free,subscription])
        self.assertEqual(d['action'],'defer')
        self.assertEqual(d['wake_in_minutes'],60)

    def test_all_family_use_combinations(self):
        for family in router.FAMILIES:
            for use in ['internal','customer','payout']:
                d=router.choose(dict(self.request,family=family,use=use),self.resources)
                self.assertEqual(d['action'],'run')
                self.assertEqual(d['resource'],'groq:openai/gpt-oss-120b')
                if use!='internal':self.assertNotEqual(d['checks'],'none')


if __name__=='__main__':
    unittest.main()
