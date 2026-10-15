import pytest
from engine import load_methods,assess,economic_assessment,scenario_total

def test_eight_methods():
    ms=load_methods();assert len(ms)==8;assert [m['id'] for m in ms]==[f'M{i}' for i in range(1,9)]

def test_data_and_mrl_gates():
    m=load_methods()[0]
    assert not assess(m,[],4)['technically_possible']
    assert not assess(m,m['required_data'],m['min_mrl']-1)['technically_possible'] if m['min_mrl']>1 else True
    assert assess(m,m['required_data'],m['min_mrl'])['technically_possible']
    assert assess(m,m['required_data'],m['min_mrl'])['status']=='fachliche Eignung offen'

def test_w_stages():
    assert economic_assessment('Zusatzprüfung','R4')['status']=='W0'
    assert economic_assessment('Zusatzprüfung','R4',2)['status']=='W1'
    r=economic_assessment('Zusatzprüfung','R4',2,30)
    assert r['status']=='W2' and r['cost']==60
    assert economic_assessment('', 'R4',2,30)['status']=='nicht begonnen'

def test_no_fake_total():
    assert scenario_total([{'status':'W2','cost':10},{'status':'W1','cost':None}]) is None
    assert scenario_total([{'status':'W2','cost':10},{'status':'W2','cost':15}])==25

def test_negative_rejected():
    with pytest.raises(ValueError):economic_assessment('x','R1',-1)
