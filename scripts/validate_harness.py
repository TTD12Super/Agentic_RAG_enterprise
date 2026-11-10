#!/usr/bin/env python3
"""Validate scaffold docs, Codex TOML and the task DAG; no external dependencies."""
from __future__ import annotations
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'AGENTS.md', 'README.md', 'GOALS.md', 'PLANS.md', 'PROMPTS.md',
    '.codex/config.toml', 'docs/architecture/overview.md',
    'docs/contracts/README.md', 'harness/tasks/tasks.json',
    'harness/handoffs/TEMPLATE.md', 'docs/security/threat-model.md',
    'docs/architecture/decisions/DECISION-REGISTER.md',
    'docs/requirements/functional-requirements.md',
    'docs/requirements/non-functional-requirements.md',
]
MANIFEST_REQUIRED = [
    'diagram.md',
    'docs/architecture/decisions/DECISION-REGISTER.md',
    'docs/architecture/overview.md',
    'docs/database/database.md',
    'docs/requirements/functional-requirements.md',
    'docs/requirements/non-functional-requirements.md',
    'docs/requirements/owner-decision-baseline.md',
    'PROJECT_TREE.md',
    'harness/tasks/tasks.json',
    'docs/design/UI:UX reference/enterprise_knowledge_ai/DESIGN.md',
]
VALID_STATUS = {'PLANNED','READY','IN_PROGRESS','BLOCKED','READY_FOR_INTEGRATION','DONE','FAILED'}
TASK_FIELDS = {'id', 'phase', 'title', 'owner', 'status', 'depends_on', 'deliverables', 'acceptance', 'scope', 'architecture_blocks', 'requirements', 'contracts', 'validation', 'handoff'}
SCOPE_FIELDS = {'read_paths', 'write_paths', 'forbidden_paths'}
DECISION_AUTHORITY_FIELDS = {'review', 'edit', 'approve'}
ERRORS = []
for f in REQUIRED:
    if not (ROOT / f).is_file(): ERRORS.append(f'Missing required file: {f}')
try:
    manifest = json.loads((ROOT / 'harness/file-manifest.json').read_text())
    manifest_files = set(manifest.get('files', []))
    for f in MANIFEST_REQUIRED:
        if f not in manifest_files: ERRORS.append(f'Manifest missing canonical file: {f}')
except (OSError, ValueError, TypeError, AttributeError) as e:
    ERRORS.append(f'Invalid file manifest: {e}')
block_files = sorted((ROOT / 'docs/architecture/blocks').glob('*.md'))
if len(block_files) != 17: ERRORS.append(f'Expected 17 block specs, found {len(block_files)}')
try:
    tomllib.loads((ROOT / '.codex/config.toml').read_text())
except (OSError, ValueError) as e: ERRORS.append(f'Invalid Codex config: {e}')
roles = sorted((ROOT / '.codex/agents').glob('*.toml'))
if len(roles) != 8: ERRORS.append(f'Expected 8 custom agents, found {len(roles)}')
for p in roles:
    try:
        data=tomllib.loads(p.read_text())
        for key in ('name','description','developer_instructions'):
            if not isinstance(data.get(key),str) or not data[key].strip(): ERRORS.append(f'{p.name}: missing {key}')
    except (OSError,ValueError) as e: ERRORS.append(f'Invalid TOML {p.name}: {e}')
try:
    task_data=json.loads((ROOT/'harness/tasks/tasks.json').read_text())
    decision_policy = task_data.get('decision_policy', {})
    expected_policy = {
        'minor_decisions': 'main_agent',
        'major_decisions': 'project_owner',
        'record': 'harness/handoffs/TASK-ID.md',
        'escalate_when': [
            'no approved option exists',
            'options have material security, privacy, cost, architecture or availability trade-offs',
            'the decision changes shared behavior or MVP scope'
        ]
    }
    if decision_policy != expected_policy: ERRORS.append('Invalid task decision_policy')
    role_map = task_data.get('agent_role_map', {})
    if role_map != {'tech_lead': 'main_agent'}: ERRORS.append('Invalid agent_role_map')
    concurrency_policy = task_data.get('concurrency_policy', {})
    expected_concurrency_policy = {
        'global_max_active_agents': 10,
        'default_active_agents': 1,
        'context_isolation': 'separate_context_per_agent',
        'activation': 'task_specific_manual'
    }
    if concurrency_policy != expected_concurrency_policy: ERRORS.append('Invalid concurrency_policy')
    task_concurrency = task_data.get('task_concurrency', {})
    if not isinstance(task_concurrency, dict): ERRORS.append('Invalid task_concurrency')
    tasks=task_data['tasks']
    specialist_roles = {p.stem for p in roles}
    valid_owners = specialist_roles | set(role_map)
    ids=[t['id'] for t in tasks]
    if len(ids)!=len(set(ids)): ERRORS.append('Duplicate task IDs')
    lookup={t['id']:t for t in tasks}
    requirement_ids = set()
    for path in ('docs/requirements/functional-requirements.md', 'docs/requirements/non-functional-requirements.md'):
        requirement_ids.update(re.findall(r'\b(?:FR|NFR)-[A-Z]+-\d+\b', (ROOT / path).read_text()))
    assigned_requirements = {req for task in tasks for req in task.get('requirements', []) if isinstance(req, str)}
    for req in sorted(requirement_ids - assigned_requirements):
        ERRORS.append(f'Requirement is not assigned to any task: {req}')
    for req in sorted(assigned_requirements - requirement_ids):
        ERRORS.append(f'Task references unknown requirement: {req}')
    task_id_by_mermaid = {task_id.replace('-', '_'): task_id for task_id in lookup}
    dependency_doc = ROOT / 'harness/tasks/DEPENDENCIES.md'
    if not dependency_doc.is_file():
        ERRORS.append('Missing dependency graph document')
    else:
        documented_edges = set()
        edge_pattern = r'\s+([A-Z]+(?:_[A-Z]+)*_\d+)\s+-->\s+([A-Z]+(?:_[A-Z]+)*_\d+)'
        for source, target in re.findall(edge_pattern, dependency_doc.read_text()):
            if source in task_id_by_mermaid and target in task_id_by_mermaid:
                documented_edges.add((task_id_by_mermaid[source], task_id_by_mermaid[target]))
        expected_edges = {(dependency, task['id']) for task in tasks for dependency in task.get('depends_on', [])}
        for edge in sorted(expected_edges - documented_edges):
            ERRORS.append(f'Dependency graph missing edge: {edge[0]} -> {edge[1]}')
        for edge in sorted(documented_edges - expected_edges):
            ERRORS.append(f'Dependency graph has extra edge: {edge[0]} -> {edge[1]}')
    overview = ROOT / 'docs/architecture/overview.md'
    register = ROOT / 'docs/architecture/decisions/DECISION-REGISTER.md'
    if overview.is_file() and register.is_file():
        register_ids = set(re.findall(r'^\| (DEC-\d+) \|', register.read_text(), re.MULTILINE))
        referenced_ids = set()
        architecture_rows = 0
        for line in overview.read_text().splitlines():
            if not line.startswith('| ARCH-P'):
                continue
            columns = [column.strip() for column in line.strip().strip('|').split('|')]
            architecture_rows += 1
            refs = set(re.findall(r'DEC-\d+', columns[-1])) if len(columns) >= 4 else set()
            referenced_ids.update(refs)
            if not refs:
                ERRORS.append(f'Architecture decision row {columns[0]} has no decision-register reference')
            for decision_id in refs:
                if decision_id not in register_ids:
                    ERRORS.append(f'Architecture decision row {columns[0]} references missing {decision_id}')
        if architecture_rows != 12:
            ERRORS.append(f'Expected 12 architecture decision rows, found {architecture_rows}')
        for decision_id in sorted(register_ids - referenced_ids):
            ERRORS.append(f'Decision register entry is not mapped from architecture overview: {decision_id}')
    for task in tasks:
        task_id = task.get('id', '?')
        phase = task.get('phase')
        checklist = ROOT / f'harness/checklists/phase-{phase}.md'
        if not checklist.is_file():
            ERRORS.append(f'Task {task_id} has no checklist for phase {phase}')
        elif task_id not in checklist.read_text():
            ERRORS.append(f'Task {task_id} is missing from phase-{phase} checklist')
    if set(task_concurrency) != set(lookup): ERRORS.append('task_concurrency must contain exactly every task ID')
    for task_id, settings in task_concurrency.items():
        requested = settings.get('requested_agents') if isinstance(settings, dict) else None
        if not isinstance(requested, int) or not 1 <= requested <= concurrency_policy.get('global_max_active_agents', 0):
            ERRORS.append(f"Invalid requested_agents for task: {task_id}")
    for t in tasks:
        if t.get('owner') not in valid_owners: ERRORS.append(f"Task {t.get('id','?')} has unknown owner: {t.get('owner')}")
        missing = sorted(TASK_FIELDS - set(t))
        if missing: ERRORS.append(f"Task {t.get('id','?')} missing fields: {', '.join(missing)}")
        scope = t.get('scope', {})
        if not isinstance(scope, dict) or set(scope) != SCOPE_FIELDS:
            ERRORS.append(f"Task {t.get('id','?')} has invalid scope; expected read_paths, write_paths, forbidden_paths")
        else:
            for scope_key in ('read_paths', 'write_paths', 'forbidden_paths'):
                if not isinstance(scope[scope_key], list) or any(not isinstance(p, str) or not p.strip() for p in scope[scope_key]):
                    ERRORS.append(f"Task {t['id']} has invalid scope.{scope_key}")
            for path_key in ('read_paths', 'write_paths'):
                for path in scope[path_key]:
                    if not (ROOT / path).exists(): ERRORS.append(f"Task {t['id']} references missing {path_key}: {path}")
        if not isinstance(t.get('architecture_blocks'), list) or not t.get('architecture_blocks'):
            ERRORS.append(f"Task {t.get('id','?')} must name architecture_blocks")
        else:
            for block in t['architecture_blocks']:
                if block not in {f'{n:02d}' for n in range(1, 18)}: ERRORS.append(f"Task {t['id']} has unknown architecture block: {block}")
        for list_key in ('requirements', 'validation'):
            if not isinstance(t.get(list_key), list) or not t.get(list_key): ERRORS.append(f"Task {t.get('id','?')} must provide {list_key}")
        if not isinstance(t.get('contracts'), list): ERRORS.append(f"Task {t.get('id','?')} must provide contracts")
        for contract in t.get('contracts', []):
            if not (ROOT / contract).is_file(): ERRORS.append(f"Task {t['id']} references missing contract: {contract}")
        handoff = t.get('handoff')
        if not isinstance(handoff, str) or not handoff.startswith('harness/handoffs/') or not (ROOT / 'harness/handoffs').is_dir():
            ERRORS.append(f"Task {t.get('id','?')} has invalid handoff path")
        if 'decision_authority' in t:
            authority = t['decision_authority']
            if not isinstance(authority, dict) or set(authority) != DECISION_AUTHORITY_FIELDS or any(not isinstance(v, str) or not v.strip() for v in authority.values()):
                ERRORS.append(f"Task {t.get('id','?')} has invalid decision_authority")
        if t.get('status') not in VALID_STATUS: ERRORS.append(f"Unknown status {t['id']}")
        for dep in t.get('depends_on',[]):
            if dep not in lookup: ERRORS.append(f"Unknown dependency {t['id']} -> {dep}")
            elif isinstance(t.get('phase'), int) and isinstance(lookup[dep].get('phase'), int) and lookup[dep]['phase'] > t['phase']:
                ERRORS.append(f"Task {t['id']} depends on later-phase task {dep}")
    active=set(); visited=set()
    def dfs(node):
        if node in active:
            ERRORS.append(f'Cycle in task dependencies at {node}'); return
        if node in visited: return
        active.add(node)
        for dep in lookup[node]['depends_on']:
            if dep in lookup: dfs(dep)
        active.remove(node); visited.add(node)
    for task_id in lookup: dfs(task_id)
    for t in tasks:
        if t['status']=='READY' and any(lookup[d]['status']!='DONE' for d in t['depends_on'] if d in lookup):
            ERRORS.append(f"Task {t['id']} READY but upstream not DONE")
except (OSError,ValueError,KeyError,TypeError) as e:
    ERRORS.append(f'Invalid task registry: {e}')

if ERRORS:
    print('HARNESS INVALID')
    for err in ERRORS: print(' -',err)
    sys.exit(1)
print(f'HARNESS VALID: {len(block_files)} blocks, {len(roles)} agents, {len(tasks)} tasks; no dependency cycles')
print('Note: this validates scaffolding only, not application functionality, permissions or the Codex runtime.')
