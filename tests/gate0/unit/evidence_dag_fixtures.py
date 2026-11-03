"""Task 1-only fixtures derived from the approved V7 plan contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PLAN_PATH = Path("docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md")

from gate0.feasibility.macos_stage_b_evidence_constants import TestContractError

HELPER_OWNER_MANIFEST = (
    {"owner":"tests/gate0/unit/evidence_dag_fixtures.py","name":"evidence_dag_authority","signature":"evidence_dag_authority() -> AuthorityTuple"},
    {"owner":"tests/gate0/unit/evidence_dag_fixtures.py","name":"mutate_lower_hex","signature":"mutate_lower_hex(value: str) -> str"},
)


def _constants():
    from gate0.feasibility import macos_stage_b_evidence_constants as c
    return c


def evidence_dag_authority():
    c = _constants()
    return c.AuthorityTuple("1"*40, "2"*40, "3"*40, "4"*40, 1)


def mutate_lower_hex(value: str) -> str:
    if not value or any(ch not in "0123456789abcdef" for ch in value):
        raise TestContractError("expected lowercase hexadecimal")
    return ("1" if value[0] != "1" else "0") + value[1:]


@dataclass(frozen=True)
class PlanContractFixture:
    path: Path
    parser: object

    def enum_values(self, name): return self.parser.enum_values(name)
    def protocol(self, name): return self.parser.protocol(name)
    def expand_expected_new_test_node_ids(self): return self.parser.expand_expected_new_test_node_ids()
    def unbound_fixture_references(self): return self.parser.unbound_fixture_references()
    def effect_policy_mapping(self): return self.parser.effect_policy_mapping()
    def effect_policy(self): return self.parser.effect_policy()
    def allowed_commands(self): return self.parser.allowed_commands()
    def allowed_command(self, task_step_id): return self.parser.allowed_command(task_step_id)
    def stdin_block_bytes(self, block_id): return self.parser.stdin_block_bytes(block_id)
    def effect_scanner_source_contract_bytes(self): return self.parser.effect_scanner_source_contract_bytes()


import pytest


def capture_bundle_bytes(wrong_blob_magic=None):
    """Return deterministic local-only source bytes for Task-3 capture tests."""
    import hashlib
    import struct

    info = b'<?xml version="1.0"?><plist version="1.0"><dict/></plist>'
    resources = b'<?xml version="1.0"?><plist version="1.0"><dict><key>files</key><dict/></dict></plist>'

    def blob(magic, payload):
        return struct.pack(">II", magic, 8 + len(payload)) + payload

    requirements = blob(0xFADE0C01, b"SYNTHETIC_REQUIREMENTS_PREIMAGE")
    entitlements = blob(0xFADE7171, info)
    der = blob(0xFADE7172, b"\x30\x00")
    cms = blob(0xFADE0B01, b"SYNTHETIC_CMS_PREIMAGE")
    ident = b"synthetic\x00"
    hash_offset = 44 + len(ident) + 7 * 32
    cd_length = hash_offset + 32
    signature_length = 52 + cd_length + sum(map(len, (requirements, entitlements, der, cms)))
    header = struct.pack("<IiiIIIII", 0xFEEDFACF, 0x0100000C, 0, 2, 1, 16, 0, 0)
    command = struct.pack("<IIII", 0x1D, 16, 512, signature_length)
    code = (header + command).ljust(512, b"\x00")
    special = {
        1: hashlib.sha256(info).digest(),
        2: hashlib.sha256(requirements).digest(),
        3: hashlib.sha256(resources).digest(),
        4: bytes(32),
        5: hashlib.sha256(entitlements).digest(),
        6: bytes(32),
        7: hashlib.sha256(der).digest(),
    }
    code_directory = struct.pack(
        ">9I4BI", 0xFADE0C02, cd_length, 0x20001, 0, hash_offset, 44,
        7, 1, 512, 32, 2, 0, 12, 0,
    )
    code_directory += ident + b"".join(special[i] for i in range(7, 0, -1))
    code_directory += hashlib.sha256(code).digest()
    blobs = ((0, code_directory), (2, requirements), (5, entitlements), (7, der), (0x10000, cms))
    offset = 52
    entries = []
    for kind, raw in blobs:
        entries.append(struct.pack(">II", kind, offset))
        offset += len(raw)
    index = struct.pack(">III", 0xFADE0CC0, offset, 5) + b"".join(entries)
    executable = code + index + b"".join(raw for _, raw in blobs)
    if wrong_blob_magic is not None:
        slot_type, wrong_magic, special_slot = wrong_blob_magic
        mutated = bytearray(executable)
        signature_offset = 512
        target_offset = None
        code_directory_offset = None
        for index_number in range(5):
            current_type, blob_offset = struct.unpack_from(">II", mutated,
                                                            signature_offset + 12 + index_number * 8)
            if current_type == slot_type:
                target_offset = blob_offset
            if current_type == 0:
                code_directory_offset = blob_offset
        if target_offset is None or code_directory_offset is None:
            raise AssertionError("synthetic superblob fixture lacks requested slot")
        absolute_target = signature_offset + target_offset
        struct.pack_into(">I", mutated, absolute_target, wrong_magic)
        if special_slot is not None:
            absolute_cd = signature_offset + code_directory_offset
            hash_offset = struct.unpack_from(">I", mutated, absolute_cd + 16)[0]
            blob_length = struct.unpack_from(">I", mutated, absolute_target + 4)[0]
            digest = hashlib.sha256(mutated[absolute_target:absolute_target + blob_length]).digest()
            struct.pack_into(">32s", mutated,
                             absolute_cd + hash_offset - special_slot * 32, digest)
        executable = bytes(mutated)
    expected = {
        "executable_code_region_bytes": code,
        "info_plist_bytes": info,
        "code_resources_bytes": resources,
        "superblob_index_bytes": index,
        "code_directory_bytes": code_directory,
        "entitlements_blob_bytes": entitlements,
        "der_entitlements_blob_bytes": der,
        "requirements_blob_sha256": hashlib.sha256(requirements).hexdigest(),
        "cms_signature_blob_sha256": hashlib.sha256(cms).hexdigest(),
    }
    return executable, info, resources, expected


def write_capture_bundle(application_path, wrong_blob_magic=None):
    executable, info, resources, expected = capture_bundle_bytes(wrong_blob_magic)
    (application_path / "Contents/MacOS").mkdir(parents=True)
    (application_path / "Contents/_CodeSignature").mkdir()
    (application_path / "Contents/MacOS/StageBSandboxRunner").write_bytes(executable)
    (application_path / "Contents/Info.plist").write_bytes(info)
    (application_path / "Contents/_CodeSignature/CodeResources").write_bytes(resources)
    return expected

@pytest.fixture
def evidence_dag_plan_contract():
    c = _constants()
    path = PLAN_PATH
    return PlanContractFixture(path, c.load_plan_contract(path))


def load_plan_contract(path):
    c = _constants()
    return c.load_plan_contract(path)


def exact_ledger_pair_for(allowed, control_inputs=None):
    c = _constants()
    return c.exact_ledger_pair_for(allowed, control_inputs)


def exact_controlled_run_ledger_for(contract, phase, base_sha, plan_blob):
    c = _constants()
    return c.exact_controlled_run_ledger_for(contract.parser, phase, base_sha, plan_blob)


def scan_synthetic_effect_source(source):
    c = _constants()
    return c.scan_synthetic_effect_source(source)


def verify_effect_scanner_source_contract(plan_path, scanner_path):
    c = _constants()
    return c.verify_effect_scanner_source_contract(plan_path, scanner_path)


def verify_approved_plan_identity(repository_root, plan_path, expected_blob):
    c = _constants()
    return c.verify_approved_plan_identity(repository_root, plan_path, expected_blob)


def write_effect_policy_variant(tmp_path, contract, mode, field):
    c = _constants()
    return c.write_effect_policy_variant(tmp_path, contract.parser, mode, field)


def write_scanner_contract_fixture(tmp_path, source):
    c = _constants()
    return c.write_scanner_contract_fixture(tmp_path, source)

from gate0.feasibility.macos_stage_b_evidence_constants import EffectPolicy, EffectKind, EffectScanFinding, EffectScanResult, scan_production_effects


# Independent literal oracle copied from the pinned Task-5 successor spec.
# Keep this separate from production serialization so expected bytes cannot
# drift with the implementation under test.
CANONICAL_IDENTITY_JSON_FIXTURE = b'{"cms_signature_blob_sha256":"8888888888888888888888888888888888888888888888888888888888888888","code_directory_identity":{"code_limit":3,"code_slot_sha256":["2222222222222222222222222222222222222222222222222222222222222222"],"page_size":4096,"sha256":"1111111111111111111111111111111111111111111111111111111111111111","special_slot_sha256":[{"sha256":"3333333333333333333333333333333333333333333333333333333333333333","slot":-1},{"sha256":"4444444444444444444444444444444444444444444444444444444444444444","slot":-2},{"sha256":"5555555555555555555555555555555555555555555555555555555555555555","slot":-3},{"sha256":null,"slot":-4},{"sha256":"6666666666666666666666666666666666666666666666666666666666666666","slot":-5},{"sha256":null,"slot":-6},{"sha256":"7777777777777777777777777777777777777777777777777777777777777777","slot":-7}]},"members":{"code_directory":"CodeDirectory","code_resources":"CodeResources","der_entitlements_blob":"DER-Entitlements.blob","entitlements_blob":"Entitlements.blob","executable_code_region":"executable-code-region.bin","identity":"identity.json","info_plist":"Info.plist","superblob_index":"superblob-index.bin"},"n4a_boundary_primitive":{"format":"N4A_BOUNDARY_PRIMITIVE_V1","renderer_input_octets":12,"renderer_input_sha256":"9999999999999999999999999999999999999999999999999999999999999999","signer_entitlements_octets":5,"signer_entitlements_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"requirements_blob_sha256":"4444444444444444444444444444444444444444444444444444444444444444","schema_version":"G0_S9_IDENTITY_V1","source_member_mapping":{"code_directory":"LC_CODE_SIGNATURE.superblob.type=CodeDirectory","code_resources":"Contents/_CodeSignature/CodeResources","der_entitlements_blob":"LC_CODE_SIGNATURE.superblob.type=DER-Entitlements","entitlements_blob":"LC_CODE_SIGNATURE.superblob.type=Entitlements","executable_code_region":"Contents/MacOS/StageBSandboxRunner@[0,codeLimit)","identity":"S9/identity.json","info_plist":"Contents/Info.plist","superblob_index":"Contents/MacOS/StageBSandboxRunner@LC_CODE_SIGNATURE.dataoff[0,52)"}}'

# BEGIN G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1
def scan_production_effects(policy: EffectPolicy) -> EffectScanResult:
    import ast
    from pathlib import Path

    def rule_matches(rule: str, symbol: str) -> bool:
        if rule.endswith("*"):
            return symbol.startswith(rule[:-1])
        return symbol == rule

    def canonical_module_name(path_text: str) -> str:
        return Path(path_text).stem

    local_roots = {
        canonical_module_name(path_text)
        for path_text in policy.production_roots
    }
    local_import_aliases: dict[str, str] = {}
    for path_text in policy.production_roots:
        canonical = canonical_module_name(path_text)
        local_import_aliases[canonical] = canonical
        if path_text.startswith("src/") and path_text.endswith(".py"):
            dotted_name = path_text[len("src/"):-len(".py")].replace("/", ".")
            local_import_aliases[dotted_name] = canonical

    def canonical_local_module(name: str) -> str | None:
        return local_import_aliases.get(name)

    def namespace_root(rule: str) -> str:
        return rule.rstrip("*").split(".", 1)[0]

    recognized_effect_roots = {
        *[namespace_root(rule) for rule in policy.process_effect_rules],
        *[namespace_root(rule) for rule in policy.traversal_effect_rules],
    }

    def is_safe_import(name: str) -> bool:
        root = name.split(".", 1)[0]
        return (
            canonical_local_module(name) is not None
            or root in recognized_effect_roots
            or any(
                name == prefix
                or name.startswith(prefix + ".")
                or (prefix.endswith("_") and name.startswith(prefix))
                for prefix in policy.safe_import_prefixes
            )
        )

    def classify(symbol: str, *, shell_true: bool) -> EffectKind | None:
        if shell_true and symbol.startswith("subprocess."):
            return EffectKind.EFFECT_UNKNOWN
        if any(
            symbol == prefix or symbol.startswith(prefix + ".")
            for prefix in policy.forbidden_network_prefixes
        ):
            return EffectKind.NETWORK
        if symbol.startswith("subprocess."):
            return EffectKind.PROCESS
        if any(rule_matches(rule, symbol) for rule in policy.process_effect_rules):
            return EffectKind.PROCESS
        if symbol == "multiprocessing" or symbol.startswith("multiprocessing."):
            return EffectKind.EFFECT_UNKNOWN
        if any(rule_matches(rule, symbol) for rule in policy.traversal_effect_rules):
            return EffectKind.TRAVERSAL
        if symbol.startswith("os."):
            if symbol in policy.os_harmless_call_allowlist:
                return None
            return EffectKind.EFFECT_UNKNOWN
        if symbol.startswith("asyncio."):
            if symbol in policy.asyncio_harmless_call_allowlist:
                return None
            return EffectKind.EFFECT_UNKNOWN
        if symbol.startswith("Path."):
            if symbol in policy.path_harmless_call_allowlist:
                return None
            return EffectKind.EFFECT_UNKNOWN
        root = symbol.split(".", 1)[0]
        if root not in local_roots and not is_safe_import(symbol):
            return EffectKind.EFFECT_UNKNOWN
        return None

    parsed: dict[str, tuple[str, ast.Module]] = {}
    module_aliases: dict[str, dict[str, str]] = {}
    import_findings: list[EffectScanFinding] = []

    for path_text in policy.production_roots:
        module_name = canonical_module_name(path_text)
        source = Path(path_text).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path_text)
        parsed[module_name] = (path_text, tree)
        aliases: dict[str, str] = {}

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    aliases[alias.asname or imported.split(".", 1)[0]] = (
                        canonical_local_module(imported) or imported
                    )
                    if any(
                        imported == prefix or imported.startswith(prefix + ".")
                        for prefix in policy.forbidden_network_prefixes
                    ):
                        import_findings.append(
                            EffectScanFinding(
                                kind=EffectKind.NETWORK,
                                module=module_name,
                                function="<module>",
                                symbol=imported,
                                line=node.lineno,
                            )
                        )
                    elif imported == "multiprocessing" or imported.startswith("multiprocessing."):
                        import_findings.append(
                            EffectScanFinding(
                                kind=EffectKind.EFFECT_UNKNOWN,
                                module=module_name,
                                function="<module>",
                                symbol=imported,
                                line=node.lineno,
                            )
                        )
                    elif not is_safe_import(imported):
                        import_findings.append(
                            EffectScanFinding(
                                kind=EffectKind.EFFECT_UNKNOWN,
                                module=module_name,
                                function="<module>",
                                symbol=imported,
                                line=node.lineno,
                            )
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_module = node.module
                for alias in node.names:
                    imported = f"{imported_module}.{alias.name}"
                    imported_module_target = canonical_local_module(imported)
                    imported_parent = canonical_local_module(imported_module)
                    if imported_module_target is not None:
                        aliases[alias.asname or alias.name] = imported_module_target
                    elif imported_parent is not None:
                        aliases[alias.asname or alias.name] = f"{imported_parent}.{alias.name}"
                    else:
                        aliases[alias.asname or alias.name] = imported
                if any(
                    imported_module == prefix or imported_module.startswith(prefix + ".")
                    for prefix in policy.forbidden_network_prefixes
                ):
                    import_findings.append(
                        EffectScanFinding(
                            kind=EffectKind.NETWORK,
                            module=module_name,
                            function="<module>",
                            symbol=imported_module,
                            line=node.lineno,
                        )
                    )
                elif imported_module == "multiprocessing" or imported_module.startswith("multiprocessing."):
                    import_findings.append(
                        EffectScanFinding(
                            kind=EffectKind.EFFECT_UNKNOWN,
                            module=module_name,
                            function="<module>",
                            symbol=imported_module,
                            line=node.lineno,
                        )
                    )
                elif not is_safe_import(imported_module):
                    import_findings.append(
                        EffectScanFinding(
                            kind=EffectKind.EFFECT_UNKNOWN,
                            module=module_name,
                            function="<module>",
                            symbol=imported_module,
                            line=node.lineno,
                        )
                    )

        module_aliases[module_name] = aliases

    direct_findings: dict[str, list[EffectScanFinding]] = {}
    local_edges: set[tuple[str, str]] = set()
    function_nodes: dict[str, tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = {}

    for module_name, (path_text, tree) in parsed.items():
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_nodes[f"{module_name}.{node.name}"] = (path_text, node)
            elif isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        function_nodes[
                            f"{module_name}.{node.name}.{member.name}"
                        ] = (path_text, member)

    local_function_names = set(function_nodes)

    for function_key, (path_text, fn) in function_nodes.items():
        module_name = function_key.split(".", 1)[0]
        function_name = function_key.split(".", 1)[1]
        owner_key = function_key.rsplit(".", 1)[0]
        aliases = dict(module_aliases[module_name])
        path_bindings: set[str] = set()

        for node in ast.walk(fn):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    aliases[alias.asname or imported.split(".", 1)[0]] = (
                        canonical_local_module(imported) or imported
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    imported = f"{node.module}.{alias.name}"
                    imported_module_target = canonical_local_module(imported)
                    imported_parent = canonical_local_module(node.module)
                    if imported_module_target is not None:
                        aliases[alias.asname or alias.name] = imported_module_target
                    elif imported_parent is not None:
                        aliases[alias.asname or alias.name] = f"{imported_parent}.{alias.name}"
                    else:
                        aliases[alias.asname or alias.name] = imported

        def dotted(expr: ast.expr) -> str | None:
            if isinstance(expr, ast.Name):
                if expr.id in path_bindings:
                    return "Path"
                value = aliases.get(expr.id, expr.id)
                if value in {"pathlib.Path", "Path"}:
                    return "Path"
                return value
            if isinstance(expr, ast.Attribute):
                if isinstance(expr.value, ast.Call):
                    ctor = dotted(expr.value.func)
                    if ctor == "Path":
                        return f"Path.{expr.attr}"
                base = dotted(expr.value)
                if base:
                    if base == "pathlib" and expr.attr == "Path":
                        return "Path"
                    return f"{base}.{expr.attr}"
            return None

        for node in ast.walk(fn):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = [node.target] if isinstance(node, ast.AnnAssign) else list(node.targets)
            value = node.value
            if not isinstance(value, ast.Call):
                continue
            ctor = dotted(value.func)
            if ctor != "Path":
                continue
            for target in targets:
                if isinstance(target, ast.Name):
                    path_bindings.add(target.id)

        direct_findings.setdefault(function_key, [])
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            symbol = dotted(node.func)
            if not symbol:
                direct_findings[function_key].append(
                    EffectScanFinding(
                        kind=EffectKind.EFFECT_UNKNOWN,
                        module=module_name,
                        function=function_name,
                        symbol="<dynamic-call>",
                        line=node.lineno,
                    )
                )
                continue

            local_target = None
            if symbol in local_function_names:
                local_target = symbol
            elif "." not in symbol:
                candidate = f"{module_name}.{symbol}"
                if candidate in local_function_names:
                    local_target = candidate
            elif symbol.startswith("self.") or symbol.startswith("cls."):
                candidate = f"{owner_key}.{symbol.split('.', 1)[1]}"
                if candidate in local_function_names:
                    local_target = candidate
            if local_target is not None:
                local_edges.add((function_key, local_target))
                continue

            shell_true = any(
                kw.arg == "shell"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value is True
                for kw in node.keywords
            )
            kind = classify(symbol, shell_true=shell_true)
            if kind is not None:
                direct_findings[function_key].append(
                    EffectScanFinding(
                        kind=kind,
                        module=module_name,
                        function=function_name,
                        symbol=symbol,
                        line=node.lineno,
                    )
                )

    propagated: dict[str, list[EffectScanFinding]] = {
        key: list(value) for key, value in direct_findings.items()
    }
    changed = True
    while changed:
        changed = False
        for caller, callee in sorted(local_edges):
            known = {
                (x.kind, x.module, x.function, x.symbol, x.line)
                for x in propagated.setdefault(caller, [])
            }
            for finding in propagated.get(callee, []):
                marker = (
                    finding.kind,
                    finding.module,
                    finding.function,
                    finding.symbol,
                    finding.line,
                )
                if marker not in known:
                    propagated[caller].append(finding)
                    known.add(marker)
                    changed = True

    all_findings = [
        *import_findings,
        *[
            item
            for values in propagated.values()
            for item in values
        ],
    ]
    findings = {
        (item.kind, item.module, item.function, item.symbol, item.line): item
        for item in all_findings
    }
    return EffectScanResult(
        findings=tuple(
            findings[key]
            for key in sorted(
                findings,
                key=lambda x: (x[1], x[2], x[4], x[3], x[0].value),
            )
        ),
        resolved_local_edges=tuple(sorted(local_edges)),
    )
# END G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1

class ExactOutcomeRecorder:
    def __init__(self):
        self.pre = []
        self.deselected = set()
        self.executed = set()
        self.phases = {}
        self.collection_errors = []
        self.outcomes = {}

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session, config, items):
        ids = [item.nodeid for item in items]
        if self.pre or len(ids) != len(set(ids)):
            raise RuntimeError("invalid collection snapshot")
        self.pre = ids

    def pytest_deselected(self, items):
        for item in items:
            self.deselected.add(item.nodeid)
            self._terminal(item.nodeid, "DESELECTED")

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors.append((report.nodeid, str(report.longrepr), "ERROR"))

    def pytest_runtest_logreport(self, report):
        self.executed.add(report.nodeid)
        self.phases.setdefault(report.nodeid, {})[report.when] = report

    def pytest_runtest_logfinish(self, nodeid, location):
        p = self.phases.get(nodeid, {})
        setup, call, teardown = p.get("setup"), p.get("call"), p.get("teardown")
        reports = [r for r in (setup, call, teardown) if r is not None]
        if (setup and setup.failed) or (teardown and teardown.failed):
            outcome = "ERROR"
        elif call and getattr(call, "wasxfail", None) and call.passed:
            outcome = "XPASSED"
        elif (
            call
            and call.failed
            and not getattr(call, "wasxfail", None)
            and isinstance(call.longrepr, str)
            and call.longrepr.startswith("[XPASS(strict)]")
        ):
            outcome = "XPASSED"
        elif any(r.skipped and getattr(r, "wasxfail", None) for r in reports):
            outcome = "XFAILED"
        elif call and call.failed:
            outcome = "FAILED"
        elif any(r.skipped for r in reports):
            outcome = "SKIPPED"
        elif call and call.passed:
            outcome = "PASSED"
        else:
            outcome = "ERROR"
        self._terminal(nodeid, outcome)

    def _terminal(self, nodeid, outcome):
        if nodeid in self.outcomes:
            raise RuntimeError(f"second terminal outcome:{nodeid}")
        self.outcomes[nodeid] = outcome

    def snapshot(self):
        pre = tuple(sorted(self.pre))
        deselected = tuple(sorted(self.deselected))
        executed = tuple(sorted(self.executed))
        missing = set(pre) - set(deselected) - set(executed)
        if missing:
            raise RuntimeError(f"collected without terminal path:{sorted(missing)}")
        return {
            "schema": "gate0-rev18-pytest-recorder.v4",
            "pre_deselection_node_ids": list(pre),
            "deselected_node_ids": list(deselected),
            "executed_node_ids": list(executed),
            "collection_errors": [list(x) for x in sorted(self.collection_errors)],
            "outcomes": dict(sorted(self.outcomes.items())),
        }

ExactOutcomeRecorder.__test__ = False
TestContractError.__test__ = False


# ==========================================================================
# Task 2 -- project-owned Mach-O parser fixtures and structural case families
#
# These helpers are derived only from the approved plan's plan-owned inventory
# and the frozen Revision-18 specification tables.  No host inspection, no
# external parser and no otool//usr/bin/file call occurs anywhere below.
# ==========================================================================

import struct as _struct

from gate0.feasibility.macos_stage_b_evidence_macho import (
    MACHO_CPU_TYPE_ARM64,
    MACHO_LOAD_COMMAND_STRUCTURE_V1,
)

_MACHO_MAGIC_64 = 0xFEEDFACF
_MACHO_SUPPORTED_THIN = b"\xcf\xfa\xed\xfe"
_MACHO_FAT32_MAGIC = b"\xca\xfe\xba\xbe"
_MACHO_FAT64_MAGIC = b"\xca\xfe\xba\xbf"


def make_thin_arm64(*, ncmds: int, commands: bytes, filetype: int = 2, flags: int = 0,
                    reserved: int = 0, cpusubtype: int = 0) -> bytes:
    """Build the minimal supported thin MH_MAGIC_64 little-endian ARM64 image."""
    header = _struct.pack(
        "<IIIIIIII", _MACHO_MAGIC_64, MACHO_CPU_TYPE_ARM64, cpusubtype, filetype,
        ncmds, len(commands), flags, reserved,
    )
    return header + commands


def _u32(value: int) -> bytes:
    return _struct.pack("<I", value)


def _command_prefix(value: int, size: int) -> bytearray:
    return bytearray(_struct.pack("<II", value, size))


def _build_command(value: int) -> bytes:
    row = MACHO_LOAD_COMMAND_STRUCTURE_V1[value]
    if value == 0x00000001:  # LC_SEGMENT, SEGMENT32, nsects=0
        return bytes(_command_prefix(value, 56) + b"\x00" * 48)
    if value == 0x00000019:  # LC_SEGMENT_64, nsects=0
        return bytes(_command_prefix(value, 72) + b"\x00" * 64)
    if value == 0x00000032:  # LC_BUILD_VERSION, ntools=0
        return bytes(_command_prefix(value, 24) + b"\x00" * 16)
    if value in (0x00000004, 0x00000005):  # LC_THREAD / LC_UNIXTHREAD, zero blocks
        return bytes(_command_prefix(value, 8))
    if row.string_offset_at is not None:
        # Exact lc_str law: the offset is fixed, the name starts immediately after
        # the fixed fields, NUL-terminates, and every remaining byte is zero.
        # The payload is chosen so the total command size is an exact 8-byte
        # multiple with the declared zero terminal padding.
        name = b"/usr/lib/dyld" if row.fixed_bytes == 12 else b"/usr/lib/libSystem.B.dylib"
        # Compute the exact command size first, then add only the minimal zero
        # terminal padding needed to reach it.
        total = ((row.fixed_bytes + len(name) + 1 + 7) // 8) * 8
        payload = name + b"\x00" + b"\x00" * (total - row.fixed_bytes - len(name) - 1)
        body = bytearray(total)
        body[0:4] = _u32(value)
        body[4:8] = _u32(len(body))
        body[row.string_offset_at:row.string_offset_at + 4] = _u32(row.fixed_bytes)
        body[row.fixed_bytes:] = payload
        return bytes(body)
    if row.string_count_at is not None:  # LC_LINKER_OPTION, count=1
        option = b"-framework\x00"
        total = ((row.fixed_bytes + len(option) + 7) // 8) * 8
        payload = option + b"\x00" * (total - row.fixed_bytes - len(option))
        body = bytearray(total)
        body[0:4] = _u32(value)
        body[4:8] = _u32(len(body))
        body[row.string_count_at:row.string_count_at + 4] = _u32(1)
        body[row.fixed_bytes:] = payload
        return bytes(body)
    if row.string_table:  # LC_IDENT, empty optional table
        return bytes(_command_prefix(value, row.fixed_bytes))
    # Fixed structure plus any declared trailing zero alignment padding.
    size = row.fixed_bytes
    if row.reserved_offsets:
        size = max(size, row.reserved_offsets[0] + 4)
    size = ((size + 7) // 8) * 8
    return bytes(_command_prefix(value, size) + b"\x00" * (size - 8))


def build_minimal_command_fixture(command_value: int) -> bytes:
    """Return the minimal valid accepted command; reject an unlisted numeric value."""
    if command_value not in MACHO_LOAD_COMMAND_STRUCTURE_V1:
        raise ValueError(f"not an accepted structural command:0x{command_value:08x}")
    return _build_command(command_value)


def _minimal_command_variant(command_value: int, variant: str) -> bytes:
    """Return a deliberately invalid variant carrying exactly one atomic structural defect."""
    row = MACHO_LOAD_COMMAND_STRUCTURE_V1[command_value]
    valid = _build_command(command_value)
    if variant == "UNDERSIZED":
        # Declare the global 8-byte minimum.  For every row whose declared minimum is
        # larger, that minimum structure is genuinely absent; the thread rows have a
        # true 8-byte zero-block minimum, so their minimal form is not a defect.
        return bytes(_command_prefix(command_value, 8))
    if variant == "FORMULA_OR_TRAILING":
        body = bytearray(valid + b"\x00" * 8)
        body[4:8] = _u32(len(body))
        return bytes(body)
    if variant == "NONZERO_RESERVED_OR_PADDING":
        defective = bytearray(valid)
        if row.reserved_offsets:
            defect = row.reserved_offsets[0]
        else:
            defect = row.fixed_bytes + valid[row.fixed_bytes:].find(b"\x00") + 1
        if defect >= len(defective):
            raise TestContractError(f"no reserved or padding byte for 0x{command_value:08x}")
        defective[defect] = 0x01
        return bytes(defective)
    raise ValueError(f"unknown structural variant:{variant}")


@dataclass(frozen=True)
class CommandExerciseResult:
    """Observed outcome of exercising one command fixture through the production parser."""
    accepted: bool
    dependency_edges: tuple = ()
    failure_code: object = None


def _is_rejected_policy_row(command_bytes: bytes) -> bool:
    """True when the numeric value is unlisted or a listed REJECT_UNSUPPORTED row."""
    from gate0.feasibility.macos_stage_b_evidence_macho import (
        MACHO_LOAD_COMMAND_POLICY_V1, _REJECT_UNSUPPORTED,
    )
    if len(command_bytes) < 4:
        return False
    value = _struct.unpack_from("<I", bytes(command_bytes), 0)[0]
    for row_value, _name, disposition in MACHO_LOAD_COMMAND_POLICY_V1:
        if row_value == value:
            return disposition is _REJECT_UNSUPPORTED
    # Any numeric value absent from the closed table is automatically rejected.
    return True


def exercise_command_fixture(command_bytes: bytes) -> CommandExerciseResult:
    """Wrap one command in one minimal thin arm64 image and invoke production parser.

    An unlisted or rejected numeric command value is a policy rejection and is
    propagated as the governed ``EvidenceDagError``.  A malformed row of the accepted
    structural table is an observed structural failure and is reported in the result.
    """
    c = _constants()
    command_bytes = bytes(command_bytes)
    from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_NATIVE_CONTAINER_PARSE_V1
    image = make_thin_arm64(ncmds=1, commands=command_bytes)
    try:
        parsed = MACHO_NATIVE_CONTAINER_PARSE_V1(image)
    except c.EvidenceDagError:
        if _is_rejected_policy_row(command_bytes):
            raise
        return CommandExerciseResult(
            accepted=False,
            dependency_edges=(),
            failure_code=c.EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID,
        )
    return CommandExerciseResult(
        accepted=True,
        dependency_edges=parsed.dependency_edges,
        failure_code=None,
    )


ACCEPTED_COMMAND_VALUES = tuple(sorted(MACHO_LOAD_COMMAND_STRUCTURE_V1))


def evidence_command_policy_table():
    """The closed 54-row numeric policy table, for oracle assertions."""
    from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_LOAD_COMMAND_POLICY_V1
    return MACHO_LOAD_COMMAND_POLICY_V1


def evidence_command_structure_table():
    """The closed 43-row accepted structural table, for oracle assertions."""
    from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_LOAD_COMMAND_STRUCTURE_V1
    return MACHO_LOAD_COMMAND_STRUCTURE_V1


def _rejected_from_policy():
    from gate0.feasibility.macos_stage_b_evidence_constants import LoadCommandDisposition
    from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_LOAD_COMMAND_POLICY_V1
    return tuple(sorted(
        value for value, _, disposition in MACHO_LOAD_COMMAND_POLICY_V1
        if disposition is LoadCommandDisposition.REJECT_UNSUPPORTED
    ))


REJECTED_COMMAND_VALUES = _rejected_from_policy()

_STRUCTURAL_VARIANTS = ("VALID", "UNDERSIZED", "FORMULA_OR_TRAILING")


@dataclass(frozen=True)
class StructuralCommandCase:
    case_id: str
    command_value: int
    variant: str
    expected_accepted: bool


def _structural_command_cases():
    cases = []
    for value in ACCEPTED_COMMAND_VALUES:
        row = MACHO_LOAD_COMMAND_STRUCTURE_V1[value]
        for variant in _STRUCTURAL_VARIANTS:
            # The thread rows declare a true 8-byte zero-block minimum, LC_IDENT
            # permits its optional bounded string table to be absent, and one extra
            # all-zero 8-byte unit is itself normatively valid for a variable-length
            # row (an empty thread block, an empty NUL-terminated string sequence, or
            # a counted-string payload plus its zero alignment padding).
            variable = (row.thread_blocks or row.string_table
                        or row.string_count_at is not None
                        or row.string_offset_at is not None)
            expected = (variant == "VALID") or (
                variant == "UNDERSIZED"
                and (row.thread_blocks or row.string_table)) or (
                variant == "FORMULA_OR_TRAILING" and variable)
            cases.append(StructuralCommandCase(
                f"0x{value:08x}-{variant}", value, variant, expected))
        if row.reserved_offsets or row.string_offset_at is not None or row.string_count_at is not None:
            cases.append(StructuralCommandCase(
                f"0x{value:08x}-NONZERO_RESERVED_OR_PADDING", value,
                "NONZERO_RESERVED_OR_PADDING", False))
    return tuple(cases)


STRUCTURAL_COMMAND_CASES = _structural_command_cases()


def build_structural_case_bytes(case: StructuralCommandCase) -> bytes:
    if case.variant == "VALID":
        return _build_command(case.command_value)
    return _minimal_command_variant(case.command_value, case.variant)


# --------------------------------------------------------------------------
# Header64 policy rows (TABLE-MACHO-HEADER64-V1)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Header64Case:
    case_id: str
    fixture_id: str
    expected_success: bool


def _header64_image(fixture_id: str) -> bytes:
    if fixture_id == "BASELINE":
        return make_thin_arm64(ncmds=0, commands=b"")
    if fixture_id == "SUBTYPE_V8":
        return make_thin_arm64(ncmds=0, commands=b"", cpusubtype=1)
    if fixture_id == "SHORT":
        return make_thin_arm64(ncmds=0, commands=b"")[:31]
    if fixture_id == "WRONG_MAGIC":
        image = bytearray(make_thin_arm64(ncmds=0, commands=b""))
        image[0:4] = b"\xce\xfa\xed\xfe"
        return bytes(image)
    if fixture_id == "WRONG_CPUTYPE":
        image = bytearray(make_thin_arm64(ncmds=0, commands=b""))
        image[4:8] = _u32(0x01000007)
        return bytes(image)
    if fixture_id == "UNSUPPORTED_SUBTYPE":
        return make_thin_arm64(ncmds=0, commands=b"", cpusubtype=2)
    if fixture_id == "UNKNOWN_SUBTYPE":
        return make_thin_arm64(ncmds=0, commands=b"", cpusubtype=0x80000000)
    if fixture_id == "REGION_OVERRUN":
        return make_thin_arm64(ncmds=0, commands=b"", reserved=0)[:32] + b""
    if fixture_id == "DECODE_ONLY_FIELDS":
        return make_thin_arm64(ncmds=0, commands=b"", filetype=0xDEADBEEF,
                               flags=0xFFFFFFFF, reserved=0x12345678)
    raise ValueError(f"unknown header64 fixture:{fixture_id}")


HEADER64_CASES = (
    Header64Case("ROW01", "BASELINE", True),
    Header64Case("ROW02", "SUBTYPE_V8", True),
    Header64Case("ROW03", "DECODE_ONLY_FIELDS", True),
    Header64Case("ROW04", "SHORT", False),
    Header64Case("ROW05", "WRONG_MAGIC", False),
    Header64Case("ROW06", "WRONG_CPUTYPE", False),
    Header64Case("ROW07", "UNSUPPORTED_SUBTYPE", False),
    Header64Case("ROW08", "UNKNOWN_SUBTYPE", False),
)


def execute_header64_case(case: Header64Case) -> bool:
    """Return the raw observed Header64 acceptance; the expectation stays in the oracle."""
    c = _constants()
    from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_NATIVE_CONTAINER_PARSE_V1
    try:
        MACHO_NATIVE_CONTAINER_PARSE_V1(_header64_image(case.fixture_id))
    except c.EvidenceDagError:
        return False
    return True


# --------------------------------------------------------------------------
# FAT outer-grammar cases
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class FatStructureCase:
    case_id: str
    fixture_id: str
    expected_success: bool


def _fat32_slice(payload: bytes, *, offset=None, size=None, align=2,
                 cputype=MACHO_CPU_TYPE_ARM64, cpusubtype=0) -> dict:
    entry = {
        "cputype": cputype, "cpusubtype": cpusubtype, "offset": offset,
        "size": size if size is not None else len(payload), "align": align,
    }
    return {"payload": payload, "entry": entry}


def _assemble_fat(magic: bytes, entries) -> bytes:
    is64 = magic == _MACHO_FAT64_MAGIC
    entry_size = 32 if is64 else 20
    metadata_end = 8 + len(entries) * entry_size
    resolved = []
    for item in entries:
        entry = dict(item["entry"])
        if entry["offset"] is None:
            entry["offset"] = metadata_end + sum(len(x["payload"]) for x in resolved)
        resolved.append({"payload": item["payload"], "entry": entry})
    header = bytearray(magic + _struct.pack(">I", len(resolved)))
    for item in resolved:
        entry = item["entry"]
        if is64:
            header += _struct.pack(
                ">IIQQII", entry["cputype"], entry["cpusubtype"],
                entry["offset"], entry["size"], entry["align"],
                entry.get("reserved", 0))
        else:
            header += _struct.pack(
                ">IIIII", entry["cputype"], entry["cpusubtype"],
                entry["offset"], entry["size"], entry["align"])
    body = bytearray(header)
    for item in resolved:
        offset = item["entry"]["offset"]
        if offset > len(body):
            body += b"\x00" * (offset - len(body))
        if offset == len(body):
            body += item["payload"]
    return bytes(body)


def _fat_fixture(fixture_id: str) -> bytes:
    good = make_thin_arm64(ncmds=0, commands=b"")
    if fixture_id == "SUPPORTED_SINGLE_ARM64":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good)])
    if fixture_id == "TRUNCATED_METADATA":
        return _MACHO_FAT32_MAGIC + _struct.pack(">I", 1)
    if fixture_id == "ZERO_SIZE":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good, size=0)])
    if fixture_id == "MATH_BOUNDS":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good, size=0xFFFFFFF0)])
    if fixture_id == "OVERLAP":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [
            _fat32_slice(good), _fat32_slice(good + b"\x00" * 8),
        ])
    if fixture_id == "ALIGN_RANGE":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good, align=64)])
    if fixture_id == "ALIGN_OFFSET":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good, offset=28, align=3)])
    if fixture_id == "FAT64_RESERVED":
        item = _fat32_slice(good)
        item["entry"]["reserved"] = 7
        return _assemble_fat(_MACHO_FAT64_MAGIC, [item])
    if fixture_id == "INNER_OUTER_MISMATCH":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good, cpusubtype=1)])
    if fixture_id == "OPAQUE_NONSELECTED":
        opaque = b"\xff" * 32
        return _assemble_fat(_MACHO_FAT32_MAGIC, [
            _fat32_slice(good),
            _fat32_slice(opaque, cputype=0x01000007, cpusubtype=3, align=2),
        ])
    if fixture_id == "GAPS":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [
            _fat32_slice(good),
            _fat32_slice(good + b"\x00" * 16, cputype=0x01000007, cpusubtype=3, align=4),
        ])
    if fixture_id == "TRAILING_BYTES":
        return _assemble_fat(_MACHO_FAT32_MAGIC, [_fat32_slice(good)]) + b"\x00" * 24
    raise ValueError(f"unknown fat fixture:{fixture_id}")


FAT_STRUCTURE_CASES = (
    FatStructureCase("TRUNCATED_METADATA", "TRUNCATED_METADATA", False),
    FatStructureCase("ZERO_SIZE", "ZERO_SIZE", False),
    FatStructureCase("MATH_BOUNDS", "MATH_BOUNDS", False),
    FatStructureCase("OVERLAP", "OVERLAP", False),
    FatStructureCase("ALIGN_RANGE", "ALIGN_RANGE", False),
    FatStructureCase("ALIGN_OFFSET", "ALIGN_OFFSET", False),
    FatStructureCase("FAT64_RESERVED", "FAT64_RESERVED", False),
    FatStructureCase("INNER_OUTER_MISMATCH", "INNER_OUTER_MISMATCH", False),
    FatStructureCase("OPAQUE_NONSELECTED", "OPAQUE_NONSELECTED", True),
    FatStructureCase("GAPS", "GAPS", True),
    FatStructureCase("TRAILING_BYTES", "TRAILING_BYTES", True),
    FatStructureCase("SUPPORTED_SINGLE_ARM64", "SUPPORTED_SINGLE_ARM64", True),
)


def execute_fat_structure_case(case: FatStructureCase) -> bool:
    """Return the raw observed FAT acceptance; the expectation stays in the oracle."""
    c = _constants()
    from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_NATIVE_CONTAINER_PARSE_V1
    try:
        MACHO_NATIVE_CONTAINER_PARSE_V1(_fat_fixture(case.fixture_id))
    except c.EvidenceDagError:
        return False
    return True


# ===========================================================================
# Task-3 census test support: V7 §5.2 dataclasses, §6 helper owners, §8.3 tables.
# Appended only; no earlier Task-1/Task-2 content is modified.
# ===========================================================================
import hashlib as _hashlib
from dataclasses import dataclass as _dataclass, replace as _replace
from pathlib import PurePath

from gate0.feasibility.macos_stage_b_evidence_constants import (
    CensusNamespaceRow,
    CensusScopeTag,
    EntryKind,
    EvidenceDagError,
    EvidenceFailureCode,
    FSEntryObservation,
    ProbeEventKind,
)
from tests.gate0.unit.evidence_dag_interface_manifest import (
    ExpectedProtocol,
    expected_protocol_from_plan_row,
)

_CENSUS_NATIVE_BYTES = make_thin_arm64(ncmds=0, commands=b"")
_CENSUS_NATIVE_BYTES_MUTATED = make_thin_arm64(ncmds=0, commands=b"", flags=1)
_CENSUS_NON_NATIVE_BYTES = b"ordinary-python-source-bytes"
_CENSUS_NON_NATIVE_BYTES_MUTATED = b"ordinary-python-source-bytes-mutated"

_CENSUS_BASE = PurePath("/census/base")
_CENSUS_VENV = PurePath("/census/venv")
_CENSUS_ELSEWHERE = PurePath("/census/elsewhere")
_CENSUS_NATIVE_PATH = _CENSUS_BASE / "lib" / "libnative.dylib"
_CENSUS_NATIVE2_PATH = _CENSUS_BASE / "lib" / "libnative2.dylib"
_CENSUS_PLAIN_PATH = _CENSUS_BASE / "plain.bin"
_CENSUS_ALIAS_PATH = _CENSUS_VENV / "bin" / "python"
_CENSUS_ALIAS_TARGET = b"../../base/lib/libnative.dylib"
_CENSUS_ALIAS_RETARGET = b"../../base/plain.bin"
_CENSUS_TRANSIENT_ALIAS_PATH = _CENSUS_VENV / "TRANSIENT_ALIAS_SENTINEL"
_CENSUS_TRANSIENT_ALIAS_TARGET = b"../base/lib/libnative.dylib"


@_dataclass(frozen=True)
class ProbeEvent:
    kind: ProbeEventKind
    subject: str
    ordinal: int
    detail: str


@_dataclass(frozen=True)
class SyntheticEntry:
    kind: EntryKind
    data: bytes | None
    raw_link_target: bytes | None


@_dataclass
class SyntheticCensusFS:
    """Injected ``CensusFS`` double that owns the observable census counters."""

    start: PurePath
    entries: dict[PurePath, SyntheticEntry]
    expansion_count: int
    read_counts: dict[PurePath, int]
    host_limit: int | None

    def __post_init__(self):
        # Observation state outside the frozen §5.2 field set.
        self.events: list[ProbeEvent] = []
        self.listed: set[PurePath] = set()
        self.lstat_seen: set[PurePath] = set()
        self.pending_mutation = None
        self.pending_mutation_id: str | None = None
        self.fired_mutation_id: str | None = None
        self.dir_symlink_traversals = 0
        self.dir_recurse_violations = 0
        self.lstat_before_readlink_violations = 0

    def _record(self, kind, subject, detail: str = "") -> None:
        self.events.append(ProbeEvent(kind, str(subject), len(self.events), detail))

    def list_entries(self, directory: PurePath) -> tuple[FSEntryObservation, ...]:
        key = PurePath(directory)
        if key in self.listed and self.pending_mutation is not None:
            hook = self.pending_mutation
            self.pending_mutation = None
            self.fired_mutation_id = self.pending_mutation_id
            hook(self)
        self.listed.add(key)
        self._record(ProbeEventKind.ENUMERATE, key)
        entry = self.entries.get(key)
        if entry is None:
            raise FileNotFoundError(str(key))
        if key not in self.lstat_seen:
            self.dir_recurse_violations += 1
        if entry.kind is EntryKind.SYMLINK:
            self.dir_symlink_traversals += 1
            raise NotADirectoryError(str(key))
        if entry.kind is not EntryKind.DIRECTORY:
            self.dir_recurse_violations += 1
            raise NotADirectoryError(str(key))
        return tuple(
            FSEntryObservation(child, self.entries[child].kind, self.entries[child].raw_link_target)
            for child in sorted(self.entries, key=lambda item: item.as_posix())
            if child.parent == key
        )

    def lstat_kind(self, path: PurePath) -> EntryKind:
        key = PurePath(path)
        entry = self.entries.get(key)
        if entry is None:
            raise FileNotFoundError(str(key))
        self.lstat_seen.add(key)
        self._record(ProbeEventKind.LSTAT, key)
        return entry.kind

    def readlink_bytes(self, path: PurePath) -> bytes:
        key = PurePath(path)
        if key not in self.lstat_seen:
            self.lstat_before_readlink_violations += 1
        entry = self.entries.get(key)
        if entry is None or entry.kind is not EntryKind.SYMLINK:
            raise OSError(f"not a symlink: {key}")
        if self.host_limit is not None and self.expansion_count >= self.host_limit:
            raise OSError(f"synthetic host symlink expansion limit: {key}")
        self.expansion_count += 1
        self._record(ProbeEventKind.READLINK, key)
        return entry.raw_link_target if entry.raw_link_target is not None else b""

    def read_file_bytes(self, path: PurePath) -> bytes:
        key = PurePath(path)
        entry = self.entries.get(key)
        if entry is None or entry.kind is not EntryKind.REGULAR_FILE:
            raise OSError(f"not a regular file: {key}")
        data = entry.data if entry.data is not None else b""
        self.read_counts[key] = self.read_counts.get(key, 0) + 1
        self._record(ProbeEventKind.READ_BYTES, key, _hashlib.sha256(data).hexdigest())
        return data

    def path_exists(self, path: PurePath) -> bool:
        return PurePath(path) in self.entries


@_dataclass
class CensusCaseFixture:
    base_root: PurePath
    venv_root: PurePath
    fs: SyntheticCensusFS
    trace: list[ProbeEvent]
    mutation_state: tuple[tuple[str, str], ...]


@_dataclass(frozen=True)
class StableCensusConstructionSpec:
    case_id: str
    fixture_builder_id: str
    subaction_ids: tuple[str, ...]
    governing_callable_id: str
    probe_observer_id: str


@_dataclass(frozen=True)
class StableCensusSubcaseExpectation:
    subaction_id: str
    expected_trace: tuple[str, ...]
    expected_success: bool
    expected_failure_code: EvidenceFailureCode | None


@_dataclass(frozen=True)
class StableCensusExpectation:
    case_id: str
    subcases: tuple[StableCensusSubcaseExpectation, ...]


@_dataclass(frozen=True)
class StableCensusObservation:
    case_id: str
    subaction_id: str
    trace: tuple[str, ...]
    success: bool
    failure_code: EvidenceFailureCode | None
    governing_call_count: int
    mutation_observed: bool


# ---------------------------------------------------------------------------
# V7 §8.2 synthetic resolver filesystems
# ---------------------------------------------------------------------------

def chain_fs(n: int, *, host_limit: int | None = None) -> SyntheticCensusFS:
    """Exactly ``n`` symlink expansions before one regular file."""
    root = PurePath("/synthetic/chain")
    entries: dict[PurePath, SyntheticEntry] = {}
    for index in range(n):
        entries[root / f"s{index}"] = SyntheticEntry(
            EntryKind.SYMLINK, None, f"s{index + 1}".encode("utf-8"),
        )
    entries[root / f"s{n}"] = SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None)
    return SyntheticCensusFS(root / "s0", entries, 0, {}, host_limit)


def cycle_fs(repeat_at_hop: int = 2) -> SyntheticCensusFS:
    """Repeat the exact first symlink pathname after ``repeat_at_hop`` expansions."""
    root = PurePath("/synthetic/cycle")
    entries: dict[PurePath, SyntheticEntry] = {}
    for index in range(repeat_at_hop):
        target = (index + 1) % repeat_at_hop
        entries[root / f"s{index}"] = SyntheticEntry(
            EntryKind.SYMLINK, None, f"s{target}".encode("utf-8"),
        )
    return SyntheticCensusFS(root / "s0", entries, 0, {}, None)


def competing_hop_cycle_fs() -> SyntheticCensusFS:
    """32 successful expansions whose next observed pathname is already visited."""
    root = PurePath("/synthetic/competing")
    entries: dict[PurePath, SyntheticEntry] = {}
    for index in range(32):
        target = index + 1 if index < 31 else 0
        entries[root / f"s{index}"] = SyntheticEntry(
            EntryKind.SYMLINK, None, f"s{target}".encode("utf-8"),
        )
    return SyntheticCensusFS(root / "s0", entries, 0, {}, None)


# ---------------------------------------------------------------------------
# Stable-census fixtures
# ---------------------------------------------------------------------------

def _census_state(fs: SyntheticCensusFS) -> tuple[tuple[str, str], ...]:
    rows = []
    for path in sorted(fs.entries, key=lambda item: item.as_posix()):
        entry = fs.entries[path]
        digest = "" if entry.data is None else _hashlib.sha256(entry.data).hexdigest()
        rows.append((path.as_posix(), f"{entry.kind.value}|{entry.raw_link_target!r}|{digest}"))
    return tuple(rows)


def _census_entries(*, symlink: bool = False, extra_native: bool = False) -> dict[PurePath, SyntheticEntry]:
    entries = {
        _CENSUS_BASE: SyntheticEntry(EntryKind.DIRECTORY, None, None),
        _CENSUS_BASE / "python3": SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None),
        _CENSUS_PLAIN_PATH: SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None),
        _CENSUS_BASE / "lib": SyntheticEntry(EntryKind.DIRECTORY, None, None),
        _CENSUS_NATIVE_PATH: SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NATIVE_BYTES, None),
        _CENSUS_BASE / "lib" / "plain.bin": SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None),
        _CENSUS_VENV: SyntheticEntry(EntryKind.DIRECTORY, None, None),
        _CENSUS_VENV / "bin": SyntheticEntry(EntryKind.DIRECTORY, None, None),
        _CENSUS_VENV / "bin" / "python3": SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None),
        _CENSUS_VENV / "site-packages": SyntheticEntry(EntryKind.DIRECTORY, None, None),
        _CENSUS_VENV / "site-packages" / "module.py": SyntheticEntry(
            EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None,
        ),
    }
    if extra_native:
        entries[_CENSUS_NATIVE2_PATH] = SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NATIVE_BYTES_MUTATED, None)
    if symlink:
        entries[_CENSUS_ALIAS_PATH] = SyntheticEntry(EntryKind.SYMLINK, None, _CENSUS_ALIAS_TARGET)
    return entries


def _census_fixture(entries: dict[PurePath, SyntheticEntry]) -> CensusCaseFixture:
    fs = SyntheticCensusFS(_CENSUS_BASE, dict(entries), 0, {}, None)
    return CensusCaseFixture(_CENSUS_BASE, _CENSUS_VENV, fs, fs.events, _census_state(fs))


def build_census_two_root_fixture() -> CensusCaseFixture:
    return _census_fixture(_census_entries())


def build_census_directory_symlink_fixture() -> CensusCaseFixture:
    entries = _census_entries()
    entries[_CENSUS_BASE / "dlink"] = SyntheticEntry(EntryKind.SYMLINK, None, b"../elsewhere")
    entries[_CENSUS_ELSEWHERE] = SyntheticEntry(EntryKind.DIRECTORY, None, None)
    entries[_CENSUS_ELSEWHERE / "TRAVERSAL_SENTINEL"] = SyntheticEntry(
        EntryKind.REGULAR_FILE, _CENSUS_NATIVE_BYTES, None,
    )
    return _census_fixture(entries)


def build_census_file_symlink_fixture() -> CensusCaseFixture:
    return _census_fixture(_census_entries(symlink=True))


def build_census_ab_mutation_fixture() -> CensusCaseFixture:
    return _census_fixture(_census_entries(symlink=True))


def build_census_native_mutation_fixture() -> CensusCaseFixture:
    return _census_fixture(_census_entries(symlink=True, extra_native=True))


def build_census_transition_fixture() -> CensusCaseFixture:
    return _census_fixture(_census_entries(extra_native=True))


def build_census_transient_state_fixture() -> CensusCaseFixture:
    entries = _census_entries()
    entries[_CENSUS_TRANSIENT_ALIAS_PATH] = SyntheticEntry(
        EntryKind.SYMLINK, None, _CENSUS_TRANSIENT_ALIAS_TARGET,
    )
    return _census_fixture(entries)


# ---------------------------------------------------------------------------
# V7 §8.3 construction actions and lookups
# ---------------------------------------------------------------------------

def _action_insert(fs: SyntheticCensusFS) -> None:
    fs.entries[_CENSUS_BASE / "lib" / "inserted.bin"] = SyntheticEntry(
        EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None,
    )


def _action_remove(fs: SyntheticCensusFS) -> None:
    fs.entries.pop(_CENSUS_NATIVE_PATH, None)


def _action_rename(fs: SyntheticCensusFS) -> None:
    entry = fs.entries.pop(_CENSUS_PLAIN_PATH, None)
    if entry is not None:
        fs.entries[_CENSUS_BASE / "plain-renamed.bin"] = entry


def _action_kind_change(fs: SyntheticCensusFS) -> None:
    fs.entries[_CENSUS_PLAIN_PATH] = SyntheticEntry(EntryKind.DIRECTORY, None, None)


def _action_retarget(fs: SyntheticCensusFS) -> None:
    if _CENSUS_ALIAS_PATH in fs.entries:
        fs.entries[_CENSUS_ALIAS_PATH] = SyntheticEntry(EntryKind.SYMLINK, None, _CENSUS_ALIAS_RETARGET)


def _action_non_native_content(fs: SyntheticCensusFS) -> None:
    fs.entries[_CENSUS_PLAIN_PATH] = SyntheticEntry(
        EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES_MUTATED, None,
    )


def _action_non_native_to_native(fs: SyntheticCensusFS) -> None:
    fs.entries[_CENSUS_PLAIN_PATH] = SyntheticEntry(EntryKind.REGULAR_FILE, _CENSUS_NATIVE_BYTES, None)


def _action_native_to_non_native(fs: SyntheticCensusFS) -> None:
    fs.entries[_CENSUS_NATIVE_PATH] = SyntheticEntry(
        EntryKind.REGULAR_FILE, _CENSUS_NON_NATIVE_BYTES, None,
    )


def _action_native_bytes(fs: SyntheticCensusFS) -> None:
    fs.entries[_CENSUS_NATIVE_PATH] = SyntheticEntry(
        EntryKind.REGULAR_FILE, _CENSUS_NATIVE_BYTES_MUTATED, None,
    )


def _action_combined(fs: SyntheticCensusFS) -> None:
    _action_insert(fs)
    _action_remove(fs)
    _action_rename(fs)
    _action_kind_change(fs)


_CENSUS_ACTIONS = {
    ("CENSUS-09", "PRIMARY"): ("CENSUS-09", _action_non_native_content),
    ("CENSUS-10", "PRIMARY"): ("CENSUS-10", _action_rename),
    ("CENSUS-12", "PRIMARY"): ("CENSUS-12", _action_native_bytes),
    ("CENSUS-13", "PRIMARY"): ("CENSUS-13", _action_non_native_content),
    ("CENSUS-14", "PRIMARY"): ("CENSUS-14", _action_non_native_content),
    ("CENSUS-15", "PRIMARY"): ("CENSUS-15", _action_non_native_to_native),
    ("CENSUS-16", "PRIMARY"): ("CENSUS-16", _action_native_to_non_native),
    ("CENSUS-17", "PRIMARY"): ("CENSUS-17", _action_native_bytes),
    ("CENSUS-18", "PRIMARY"): ("CENSUS-18", _action_retarget),
    ("CENSUS-19", "INSERT"): ("INSERT", _action_insert),
    ("CENSUS-19", "REMOVE"): ("REMOVE", _action_remove),
    ("CENSUS-19", "RENAME"): ("RENAME", _action_rename),
    ("CENSUS-19", "KIND_CHANGE"): ("KIND_CHANGE", _action_kind_change),
}

#: Canonical subject whose class transition each transition case probes.
_CENSUS_OBSERVED_SUBJECTS = {
    "CENSUS-14": _CENSUS_PLAIN_PATH,
    "CENSUS-15": _CENSUS_PLAIN_PATH,
    "CENSUS-16": _CENSUS_NATIVE_PATH,
    "CENSUS-17": _CENSUS_NATIVE_PATH,
}

_FIXTURE_BUILDERS = {
    "build_census_two_root_fixture": build_census_two_root_fixture,
    "build_census_directory_symlink_fixture": build_census_directory_symlink_fixture,
    "build_census_file_symlink_fixture": build_census_file_symlink_fixture,
    "build_census_ab_mutation_fixture": build_census_ab_mutation_fixture,
    "build_census_native_mutation_fixture": build_census_native_mutation_fixture,
    "build_census_transition_fixture": build_census_transition_fixture,
    "build_census_transient_state_fixture": build_census_transient_state_fixture,
}

_CENSUS_CONSTRUCTION_START = "### 8.3 Stable-census construction/expectation split"
_CENSUS_EXPECTATION_START = "Comparison truth is separately frozen"
_CENSUS_EXPECTATION_END = "### 8.4 Native-manifest serialization"
_CENSUS_TABLES: dict[str, object] = {}


def _census_table(key: str):
    if not _CENSUS_TABLES:
        text = PLAN_PATH.read_text(encoding="utf-8")
        json_block = _constants()._json_block
        _CENSUS_TABLES["construction"] = json_block(
            text, _CENSUS_CONSTRUCTION_START, _CENSUS_EXPECTATION_START,
        )
        _CENSUS_TABLES["expectation"] = json_block(
            text, _CENSUS_EXPECTATION_START, _CENSUS_EXPECTATION_END,
        )
    return _CENSUS_TABLES[key]


def census_construction(case_id: str) -> StableCensusConstructionSpec:
    """Exact construction lookup for CENSUS-01..21 (V7 §8.3 first table)."""
    rows = {row["case_id"]: row for row in _census_table("construction")}
    row = rows.get(case_id)
    if row is None:
        raise TestContractError(f"unknown census case:{case_id}")
    return StableCensusConstructionSpec(
        case_id=row["case_id"],
        fixture_builder_id=row["fixture_builder_id"],
        subaction_ids=tuple(row["subaction_ids"]),
        governing_callable_id=row["governing_callable_id"],
        probe_observer_id=row["probe_observer_id"],
    )


def census_expectation(case_id: str) -> StableCensusExpectation:
    """Separate expectation lookup for CENSUS-01..21 (V7 §8.3 second table)."""
    rows = {row["case_id"]: row for row in _census_table("expectation")}
    row = rows.get(case_id)
    if row is None:
        raise TestContractError(f"unknown census case:{case_id}")
    return StableCensusExpectation(
        case_id=row["case_id"],
        subcases=tuple(
            StableCensusSubcaseExpectation(
                subaction_id=sub["subaction_id"],
                expected_trace=tuple(sub["expected_trace"]),
                expected_success=bool(sub["expected_success"]),
                expected_failure_code=(
                    None if sub["expected_failure_code"] is None
                    else EvidenceFailureCode(sub["expected_failure_code"])
                ),
            )
            for sub in row["subcases"]
        ),
    )


def expectation_for_subaction(expectation: StableCensusExpectation,
                              subaction_id: str) -> StableCensusExpectation:
    matches = tuple(sub for sub in expectation.subcases if sub.subaction_id == subaction_id)
    if len(matches) != 1:
        raise TestContractError(f"subaction not present exactly once:{subaction_id}")
    return StableCensusExpectation(case_id=expectation.case_id, subcases=matches)


def compare_stable_census(observations: tuple[StableCensusObservation, ...],
                          expectation: StableCensusExpectation) -> bool:
    """External comparator only; never available to the executor."""
    if expectation is None or len(observations) != len(expectation.subcases):
        return False
    by_subaction = {observation.subaction_id: observation for observation in observations}
    if len(by_subaction) != len(observations):
        return False
    for subcase in expectation.subcases:
        observation = by_subaction.get(subcase.subaction_id)
        if observation is None:
            return False
        if tuple(observation.trace) != tuple(subcase.expected_trace):
            return False
        if observation.success != subcase.expected_success:
            return False
        if observation.failure_code is not subcase.expected_failure_code:
            return False
    return True


# ---------------------------------------------------------------------------
# V7 §8.3 independent observation
# ---------------------------------------------------------------------------

def _phase_cut(fixture: CensusCaseFixture) -> int | None:
    seen: set[str] = set()
    for event in fixture.trace:
        if event.kind is not ProbeEventKind.ENUMERATE:
            continue
        if event.subject in seen:
            return event.ordinal
        seen.add(event.subject)
    return None


def _scope_counts(rows) -> dict[CensusScopeTag, int]:
    counts: dict[CensusScopeTag, int] = {}
    for row in rows:
        counts[row.scope_tag] = counts.get(row.scope_tag, 0) + 1
    return counts


def _row_path(fixture: CensusCaseFixture, row: CensusNamespaceRow) -> PurePath:
    root = fixture.base_root if row.scope_tag is CensusScopeTag.BASE_RUNTIME else fixture.venv_root
    return root / row.relative_path_utf8.decode("utf-8")


def _law(condition: bool, token: str) -> str:
    return token if condition else f"VIOLATION:{token}"


def _all_symlinks_lstat_first(fixture: CensusCaseFixture) -> bool:
    first_lstat: dict[str, int] = {}
    first_readlink: dict[str, int] = {}
    for event in fixture.trace:
        if event.kind is ProbeEventKind.LSTAT:
            first_lstat.setdefault(event.subject, event.ordinal)
        elif event.kind is ProbeEventKind.READLINK:
            first_readlink.setdefault(event.subject, event.ordinal)
    if not first_readlink:
        return False
    return all(ordinal > first_lstat.get(subject, 1 << 60) for subject, ordinal in first_readlink.items())


def _real_directory_recursion_only(fixture: CensusCaseFixture) -> bool:
    fs = fixture.fs
    if fs.dir_symlink_traversals or fs.dir_recurse_violations:
        return False
    enumerated = [event.subject for event in fixture.trace if event.kind is ProbeEventKind.ENUMERATE]
    if not enumerated:
        return False
    lstat_seen: set[str] = set()
    for event in fixture.trace:
        if event.kind is ProbeEventKind.LSTAT:
            lstat_seen.add(event.subject)
        elif event.kind is ProbeEventKind.ENUMERATE and event.subject not in lstat_seen:
            return False
    for subject in enumerated:
        entry = fs.entries.get(PurePath(subject))
        if entry is None or entry.kind is not EntryKind.DIRECTORY:
            return False
    return True


def _namespace_grammar_ok(rows) -> bool:
    if not rows:
        return False
    for row in rows:
        if not isinstance(row.scope_tag, CensusScopeTag) or not isinstance(row.entry_kind, EntryKind):
            return False
        text = row.relative_path_utf8.decode("utf-8")
        if not text or text.startswith("/"):
            return False
        if any(part in ("", ".", "..") for part in PurePath(text).parts):
            return False
        if row.entry_kind is EntryKind.SYMLINK:
            if row.raw_link_target is None or row.canonicalization_result is None:
                return False
        elif row.raw_link_target is not None or row.canonicalization_result is not None:
            return False
        elif row.canonical_target is not None:
            return False
    return True


def _raw_targets_exact(fixture: CensusCaseFixture, rows) -> bool:
    seen = False
    for row in rows:
        if row.entry_kind is not EntryKind.SYMLINK:
            continue
        seen = True
        entry = fixture.fs.entries.get(_row_path(fixture, row))
        if entry is None or entry.raw_link_target != row.raw_link_target:
            return False
    return seen


def _resolved_target_owns_scope(fixture: CensusCaseFixture, result) -> bool:
    if result is None:
        return False
    subjects = {str(path) for path, _ in result.census_a_native_images}
    if not subjects:
        return False
    for row in result.native_manifest_rows:
        root = fixture.base_root if row.scope_tag is CensusScopeTag.BASE_RUNTIME else fixture.venv_root
        text = row.relative_path_utf8.decode("utf-8")
        if any(part in ("", ".", "..") for part in PurePath(text).parts):
            return False
        if str(root / text) not in subjects:
            return False
    return True


def _both_roots_both_phases(fixture: CensusCaseFixture) -> bool:
    cut = _phase_cut(fixture)
    if cut is None:
        return False

    def scopes(events) -> set[CensusScopeTag]:
        found: set[CensusScopeTag] = set()
        for event in events:
            if event.kind is not ProbeEventKind.ENUMERATE:
                continue
            path = PurePath(event.subject)
            if path == fixture.base_root or fixture.base_root in path.parents:
                found.add(CensusScopeTag.BASE_RUNTIME)
            elif path == fixture.venv_root or fixture.venv_root in path.parents:
                found.add(CensusScopeTag.RUN_SCOPED_VENV)
        return found

    expected = {CensusScopeTag.BASE_RUNTIME, CensusScopeTag.RUN_SCOPED_VENV}
    first = scopes([event for event in fixture.trace if event.ordinal < cut])
    second = scopes([event for event in fixture.trace if event.ordinal >= cut])
    return first == expected and second == expected


def _subject_class_by_phase(fixture: CensusCaseFixture, subject: PurePath) -> tuple[str, str]:
    """Class observed for one canonical subject in each complete census.

    The census reads a subject and then immediately classifies exactly those
    bytes, so each ``CLASSIFY`` probe event pairs with the most recent
    ``READ_BYTES`` event; the first repeated ``ENUMERATE`` marks the start of
    Census B.
    """
    cut = _phase_cut(fixture)
    last_read: str | None = None
    observed: dict[tuple[str, bool], str] = {}
    for event in fixture.trace:
        if event.kind is ProbeEventKind.READ_BYTES:
            last_read = event.subject
        elif event.kind is ProbeEventKind.CLASSIFY and last_read is not None:
            phase_a = cut is None or event.ordinal < cut
            observed[(last_read, phase_a)] = event.detail
    key = subject.as_posix()
    return observed.get((key, True), "NONE"), observed.get((key, False), "NONE")


def _census_a_read_count_per_native_is_one(fixture: CensusCaseFixture, result) -> bool:
    cut = _phase_cut(fixture)
    if result is None or cut is None or not result.census_a_native_images:
        return False
    counts: dict[str, int] = {}
    for event in fixture.trace:
        if event.kind is ProbeEventKind.READ_BYTES and event.ordinal < cut:
            counts[event.subject] = counts.get(event.subject, 0) + 1
    return all(counts.get(str(path), 0) == 1 for path, _ in result.census_a_native_images)


def _materialize_source_is_census_a(result) -> bool:
    if result is None or not result.census_a_native_images:
        return False
    digests = {_hashlib.sha256(data).hexdigest() for _, data in result.census_a_native_images}
    row_digests = {row.sha256_hex for row in result.native_manifest_rows}
    return bool(row_digests) and digests == row_digests


def _transient_state_in_serialized_bytes(fixture: CensusCaseFixture, result) -> bool:
    # CENSUS-20 observes the explicit return value of the governing serializer.
    # Keep this helper tolerant of the other census observations, which receive
    # the full stable-census result object.
    data = result if isinstance(result, bytes) else result.native_manifest_bytes
    if str(fixture.base_root).encode("utf-8") in data or str(fixture.venv_root).encode("utf-8") in data:
        return True
    if _CENSUS_TRANSIENT_ALIAS_TARGET in data or b"../" in data:
        return True
    return _CENSUS_TRANSIENT_ALIAS_PATH.name.encode("utf-8") in data


def _census_runtime():
    from gate0.feasibility import macos_stage_b_evidence_runtime as runtime
    return runtime


def _case_trace(case_id: str, fixture: CensusCaseFixture, result, error,
                classifier_ids) -> tuple[str, ...]:
    fs = fixture.fs
    rows_a = () if result is None or isinstance(result, bytes) else result.namespace_a
    reason = "" if error is None else str(error.reason)
    if case_id == "CENSUS-01":
        counts = _scope_counts(rows_a)
        return (
            _law(counts.get(CensusScopeTag.BASE_RUNTIME, 0) >= 1, "ENUMERATE:BASE_RUNTIME>=1"),
            _law(counts.get(CensusScopeTag.RUN_SCOPED_VENV, 0) >= 1, "ENUMERATE:RUN_SCOPED_VENV>=1"),
        )
    if case_id == "CENSUS-02":
        return (_law(_all_symlinks_lstat_first(fixture), "LSTAT_BEFORE_READLINK:ALL_SYMLINKS"),)
    if case_id == "CENSUS-03":
        return (_law(_real_directory_recursion_only(fixture), "DIRECTORY_RECURSE:REAL_ONLY"),)
    if case_id == "CENSUS-04":
        return (f"DIRECTORY_SYMLINK_TRAVERSAL_COUNT={fs.dir_symlink_traversals}",)
    if case_id == "CENSUS-05":
        return (_law(_raw_targets_exact(fixture, rows_a), "RAW_LINK_TARGET_BYTES_EXACT=1"),)
    if case_id == "CENSUS-06":
        symlinks = [row for row in rows_a if row.entry_kind is EntryKind.SYMLINK]
        return (_law(bool(symlinks) and all(row.canonical_target is not None for row in symlinks),
                     "CANONICAL_TARGET_RECORDED=1"),)
    if case_id == "CENSUS-07":
        return (_law(_resolved_target_owns_scope(fixture, result), "RESOLVED_TARGET_SCOPE_OWNS_ROW=1"),)
    if case_id == "CENSUS-08":
        return (_law(_namespace_grammar_ok(rows_a), "NAMESPACE_ROW_FIELDS_EXACT=1"),)
    if case_id == "CENSUS-09":
        return (_law(_phase_cut(fixture) is not None, "CENSUS_A_ENUMERATION_ID!=CENSUS_B_ENUMERATION_ID"),)
    if case_id == "CENSUS-10":
        return (_law(_both_roots_both_phases(fixture), "BOTH_ROOTS_ENUMERATED_A_B=1"),)
    if case_id == "CENSUS-11":
        first = classifier_ids[0] if classifier_ids else "NONE"
        last = classifier_ids[-1] if len(classifier_ids) > 1 else "NONE"
        return (f"CLASSIFIER_CALLABLE_ID_A={first}", f"CLASSIFIER_CALLABLE_ID_B={last}")
    if case_id == "CENSUS-12":
        return (_law(error is not None and "native digest" in reason, "NATIVE_DIGEST_A!=NATIVE_DIGEST_B"),)
    if case_id == "CENSUS-13":
        return (
            _law(_census_a_read_count_per_native_is_one(fixture, result), "CENSUS_A_READ_COUNT_PER_NATIVE=1"),
            _law(_materialize_source_is_census_a(result), "PARSE_DIGEST_MATERIALIZE_SOURCE=CENSUS_A_BYTES"),
        )
    if case_id in ("CENSUS-14", "CENSUS-15", "CENSUS-16", "CENSUS-17"):
        class_a, class_b = _subject_class_by_phase(fixture, _CENSUS_OBSERVED_SUBJECTS[case_id])
        tokens = [f"CLASS_A={class_a}", f"CLASS_B={class_b}"]
        if case_id == "CENSUS-17":
            tokens.append(_law(error is not None and "native digest" in reason, "NATIVE_DIGEST_A!=NATIVE_DIGEST_B"))
        return tuple(tokens)
    if case_id == "CENSUS-18":
        return (_law(error is not None and "namespace" in reason, "RAW_OR_CANONICAL_TARGET_A!=B"),)
    if case_id == "CENSUS-20":
        return (_law(result is not None and not _transient_state_in_serialized_bytes(fixture, result),
                     "TRANSIENT_NAMESPACE_RAWLINK_PATH_STATE_IN_SERIALIZED_BYTES=0"),)
    if case_id == "CENSUS-21":
        return (_law(not any("atomic" in name.lower() or "snapshot" in name.lower()
                             for name in dir(_census_runtime())),
                     "ATOMIC_HISTORICAL_SNAPSHOT_CLAIM_COUNT=0"),)
    raise TestContractError(f"no observation schema for case:{case_id}")


def _governing_callable(name: str):
    def _serialize_governing_call(fixture: CensusCaseFixture):
        # CENSUS-20's governing callable is ``serialize_native_manifest``. Invoke
        # the real production serializer so the governing call genuinely happens,
        # and return its explicit byte image for the observation schema below.
        runtime = _census_runtime()
        result = runtime.capture_stable_census(fixture.base_root, fixture.venv_root, fixture.fs)
        # The governing callable's returned bytes are the artifact under test.
        # Do not substitute the result object's internally populated field: a
        # serializer implementation that returns a different byte image must
        # be visible to the CENSUS-20 observer.
        return runtime.serialize_native_manifest(result)

    table = {
        "capture_stable_census": lambda fixture: _census_runtime().capture_stable_census(
            fixture.base_root, fixture.venv_root, fixture.fs,
        ),
        "serialize_native_manifest": _serialize_governing_call,
    }
    if name not in table:
        raise TestContractError(f"unknown governing callable:{name}")
    return table[name]


def _run_subaction(case_id: str, subaction_id: str, fixture: CensusCaseFixture,
                   cheat: str | None, *, fresh: bool) -> StableCensusObservation:
    construction = census_construction(case_id)
    governing_callable_id = construction.governing_callable_id
    installed = None
    if cheat not in ("NO_MUTATION", "NO_GOVERNING_CALL"):
        if cheat == "COMBINED_MUTATION":
            installed = ("COMBINED_MUTATION", _action_combined)
        else:
            installed = _CENSUS_ACTIONS.get((case_id, subaction_id))
    if installed is not None:
        fixture.fs.pending_mutation_id = installed[0]
        fixture.fs.pending_mutation = installed[1]

    runtime = _census_runtime()
    classifier_ids: list[str] = []
    result = None
    error = None
    governing_call_count = 0
    original = runtime.M1R_NATIVE_CANDIDATE_CLASSIFIER_V1

    def probe(data):
        classification = original(bytes(data))
        classifier_ids.append("M1R_NATIVE_CANDIDATE_CLASSIFIER_V1")
        fixture.trace.append(ProbeEvent(
            ProbeEventKind.CLASSIFY, _hashlib.sha256(bytes(data)).hexdigest(),
            len(fixture.trace), classification.value,
        ))
        return classification

    runtime.M1R_NATIVE_CANDIDATE_CLASSIFIER_V1 = probe
    try:
        if cheat != "NO_GOVERNING_CALL":
            governing_call_count = 1
            try:
                result = _governing_callable(governing_callable_id)(fixture)
            except EvidenceDagError as exc:
                error = exc
                result = None
    finally:
        runtime.M1R_NATIVE_CANDIDATE_CLASSIFIER_V1 = original

    if fixture.fs.fired_mutation_id is not None:
        fixture.mutation_state = _census_state(fixture.fs)
    declared = _CENSUS_ACTIONS.get((case_id, subaction_id))
    declared_action_id = declared[0] if declared is not None else None
    mutation_observed = (
        fixture.fs.fired_mutation_id is not None
        and fixture.fs.fired_mutation_id == declared_action_id
    )

    if cheat == "SYNTHESIZED_TRACE":
        trace = (
            "FRESH_FIXTURE=1",
            f"ACTION:{subaction_id}",
            f"GOVERNING_CALL:{governing_callable_id}",
            "MUTATION_OBSERVED=1",
            "RESULT:SUCCESS",
        )
        mutation_observed = True
    elif case_id == "CENSUS-19":
        tokens = []
        if fresh:
            tokens.append("FRESH_FIXTURE=1")
        tokens.append(f"ACTION:{subaction_id}")
        if governing_call_count >= 1:
            tokens.append(f"GOVERNING_CALL:{governing_callable_id}")
        if mutation_observed:
            tokens.append("MUTATION_OBSERVED=1")
        if governing_call_count >= 1:
            tokens.append(f"RESULT:{error.code.value}" if error is not None else "RESULT:SUCCESS")
        trace = tuple(tokens)
    else:
        trace = _case_trace(case_id, fixture, result, error, classifier_ids)

    return StableCensusObservation(
        case_id=case_id,
        subaction_id=subaction_id,
        trace=trace,
        success=error is None and result is not None,
        failure_code=error.code if isinstance(error, EvidenceDagError) else None,
        governing_call_count=governing_call_count,
        mutation_observed=mutation_observed,
    )


def _execute_stable_census_construction(spec: StableCensusConstructionSpec,
                                        *, cheat: str | None) -> tuple[StableCensusObservation, ...]:
    if not isinstance(spec, StableCensusConstructionSpec):
        raise TestContractError("a StableCensusConstructionSpec is required")
    construction = census_construction(spec.case_id)
    if spec.fixture_builder_id != construction.fixture_builder_id:
        raise TestContractError("fixture builder id differs from the plan construction record")
    if spec.governing_callable_id != construction.governing_callable_id:
        raise TestContractError("governing callable id differs from the plan construction record")
    if spec.probe_observer_id != construction.probe_observer_id:
        raise TestContractError("probe observer id differs from the plan construction record")
    unknown = [item for item in spec.subaction_ids if item not in construction.subaction_ids]
    if unknown:
        raise TestContractError(f"unknown subaction ids:{unknown}")

    if cheat == "NO_OP_EXECUTOR":
        return tuple(
            StableCensusObservation(spec.case_id, subaction_id, (), False, None, 0, False)
            for subaction_id in spec.subaction_ids
        )

    builder = _FIXTURE_BUILDERS.get(construction.fixture_builder_id)
    if builder is None:
        raise TestContractError(f"unknown fixture builder:{construction.fixture_builder_id}")
    shared = builder() if cheat == "REUSED_FIXTURE" else None
    return tuple(
        _run_subaction(spec.case_id, subaction_id, shared if shared is not None else builder(),
                       cheat, fresh=shared is None)
        for subaction_id in spec.subaction_ids
    )


def execute_stable_census_construction(
        spec: StableCensusConstructionSpec) -> tuple[StableCensusObservation, ...]:
    """V7 §8.3 order; no stage ever receives a ``StableCensusExpectation``."""
    return _execute_stable_census_construction(spec, cheat=None)


def run_census_cheat_falsifier(cheat: str) -> bool:
    """Replace one execution stage with a named cheat and return the comparator result."""
    if cheat not in ("NO_OP_EXECUTOR", "SYNTHESIZED_TRACE", "NO_GOVERNING_CALL", "NO_MUTATION",
                     "COMBINED_MUTATION", "REUSED_FIXTURE"):
        raise TestContractError(f"unknown census cheat:{cheat}")
    construction = census_construction("CENSUS-19")
    expectation = census_expectation("CENSUS-19")
    subactions = construction.subaction_ids[:2] if cheat == "REUSED_FIXTURE" else construction.subaction_ids[:1]
    observations = _execute_stable_census_construction(
        _replace(construction, subaction_ids=subactions), cheat=cheat,
    )
    subset = StableCensusExpectation(
        expectation.case_id,
        tuple(sub for sub in expectation.subcases if sub.subaction_id in subactions),
    )
    return compare_stable_census(observations, subset)


# ---------------------------------------------------------------------------
# V7 §5.4/§6 plan-row protocol truth
# ---------------------------------------------------------------------------

def _plan_contract_protocol(self, name: str) -> ExpectedProtocol:
    """V7 §5.4 protocol row as exact ``ExpectedProtocol`` comparison truth."""
    return expected_protocol_from_plan_row(self.parser.protocol(name))


PlanContractFixture.protocol = _plan_contract_protocol
