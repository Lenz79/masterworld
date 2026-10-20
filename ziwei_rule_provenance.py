"""V8.59 provenance gates: no historical source may be implied without verified citation."""
REQUIRED = ('id','title','stars')
ALLOWED_STATES = ('internal_observation','source_pending','source_verified')

def validate_registry(rules):
    issues=[]; seen=set()
    for i,rule in enumerate(rules):
        for key in REQUIRED:
            if not rule.get(key): issues.append(f'rule[{i}]: missing {key}')
        rid=rule.get('id')
        if rid in seen: issues.append(f'rule[{i}]: duplicate id {rid}')
        seen.add(rid)
        stars=rule.get('stars') or ()
        if len(stars)!=2 or len(set(stars))!=2: issues.append(f'rule[{i}]: requires two distinct stars')
        state=rule.get('source_status','internal_observation')
        if state not in ALLOWED_STATES: issues.append(f'rule[{i}]: invalid source status')
        if state=='source_verified' and not (rule.get('citation') and rule.get('school')):
            issues.append(f'rule[{i}]: verified source requires citation and school')
    return {'valid':not issues,'issues':issues,'rule_count':len(rules)}

def provenance(rule):
    state=rule.get('source_status','internal_observation')
    citation=rule.get('citation') if state=='source_verified' else None
    return {'source_status':state,'school':rule.get('school') if citation else None,
            'citation':citation,'traditional_definition_verified':bool(citation and rule.get('school')),
            'interpretation_ready':False,
            'review_required':['原始文献与版本页码','流派归属','亮度门槛','煞忌影响','四化配合']}
