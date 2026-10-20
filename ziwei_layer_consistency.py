"""V8.64: compare transformation evidence without treating repeated natal paths as independent."""
from collections import defaultdict

def audit_layers(analysis):
    annual=analysis.get('annual_integrity_audit') or {}
    decade=analysis.get('decade_integrity_audit') or {}
    edges=analysis.get('edges') or []
    physical=defaultdict(set)
    for e in edges:
        if e.get('layer') in ('本命','大限','流年'):
            physical[(e.get('source'),e.get('target'),e.get('gan'),e.get('hua'),e.get('star'))].add(e.get('layer'))
    reused=[{'source':k[0],'target':k[1],'gan':k[2],'hua':k[3],'star':k[4],'layers':sorted(layers)} for k,layers in physical.items() if len(layers)>1]
    return {'version':'v8.64','raw_paths':len(edges),'independent_physical_paths':len(physical),
            'reused_paths':reused,'annual_consistent':annual.get('all_consistent'),
            'decade_consistent':decade.get('all_consistent'),
            'independent_layer_confirmation':False,'event_formed':None,
            'warning':'本命宫干在限年层重复出现，不是独立印证；年度与大限落点一致性不等于流派规则校准。'}
