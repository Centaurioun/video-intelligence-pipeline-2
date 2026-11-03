"""Gate-0 Revision-18 shared evidence contracts and verifier support."""
from __future__ import annotations
import ast, dataclasses, hashlib, json, os, re, subprocess
from dataclasses import dataclass, make_dataclass
from enum import Enum
from pathlib import Path, PurePath
from typing import Any

EvidenceFailureCode = Enum('EvidenceFailureCode', {'AUTHORITY_ECHO_MISMATCH': 'AUTHORITY_ECHO_MISMATCH', 'AUTHORITY_CONSUMPTION_NOT_RECORDED': 'AUTHORITY_CONSUMPTION_NOT_RECORDED', 'GENERATION_IDENTITY_COLLISION': 'GENERATION_IDENTITY_COLLISION', 'RENDER_INPUT_NOT_FROZEN': 'RENDER_INPUT_NOT_FROZEN', 'OUTPUT_ROOT_AMBIGUOUS': 'OUTPUT_ROOT_AMBIGUOUS', 'PREBUILD_ANCHOR_NOT_FROZEN': 'PREBUILD_ANCHOR_NOT_FROZEN', 'FROZEN_EVIDENCE_MUTATED_BY_BUILD': 'FROZEN_EVIDENCE_MUTATED_BY_BUILD', 'ANCHOR_DIGEST_NOT_RECORDED': 'ANCHOR_DIGEST_NOT_RECORDED', 'BUILD_OUTPUT_SEAL_NOT_FROZEN': 'BUILD_OUTPUT_SEAL_NOT_FROZEN', 'SEAL_IDENTITY_HOME_INCOMPLETE': 'SEAL_IDENTITY_HOME_INCOMPLETE', 'SIGNING_ENTITLEMENTS_NOT_FROZEN': 'SIGNING_ENTITLEMENTS_NOT_FROZEN', 'SIGNING_IDENTITY_DRIFT': 'SIGNING_IDENTITY_DRIFT', 'SIGNED_BYTES_NOT_VERIFIER_DERIVED': 'SIGNED_BYTES_NOT_VERIFIER_DERIVED', 'ENTITLEMENT_ALLOWLIST_VIOLATION': 'ENTITLEMENT_ALLOWLIST_VIOLATION', 'ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE': 'ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE', 'S8_NOT_RETAINED_EXACTLY': 'S8_NOT_RETAINED_EXACTLY', 'POLICY_CLOSURE_RESULT_NOT_RECORDED': 'POLICY_CLOSURE_RESULT_NOT_RECORDED', 'SEAL_PROJECTION_ELISION_INVALID': 'SEAL_PROJECTION_ELISION_INVALID', 'SEAL_PROJECTION_PRIVACY_VIOLATION': 'SEAL_PROJECTION_PRIVACY_VIOLATION', 'RENDER_NOT_BYTE_REPRODUCIBLE': 'RENDER_NOT_BYTE_REPRODUCIBLE', 'REPRODUCIBILITY_PROOF_VACUOUS': 'REPRODUCIBILITY_PROOF_VACUOUS', 'RESULT_MANIFEST_NOT_FINAL': 'RESULT_MANIFEST_NOT_FINAL', 'EVIDENCE_PACKAGE_NOT_ADDITIVE': 'EVIDENCE_PACKAGE_NOT_ADDITIVE', 'EVIDENCE_NOT_RETAINED': 'EVIDENCE_NOT_RETAINED', 'EVIDENCE_REFERENCE_UNRESOLVED': 'EVIDENCE_REFERENCE_UNRESOLVED', 'DEPENDENCY_INVENTORY_DERIVATION_INVALID': 'DEPENDENCY_INVENTORY_DERIVATION_INVALID', 'GENERATION_B_TIER1_GATE_UNMET': 'GENERATION_B_TIER1_GATE_UNMET', 'GATE_COVERAGE_INCOMPLETE': 'GATE_COVERAGE_INCOMPLETE', 'ENVELOPE_REFERENCE_NOT_ACCEPTED': 'ENVELOPE_REFERENCE_NOT_ACCEPTED'})
NativeCandidateClassification = Enum('NativeCandidateClassification', {'NON_NATIVE': 'NON_NATIVE', 'UNSUPPORTED_MACHO_CANDIDATE': 'UNSUPPORTED_MACHO_CANDIDATE', 'NATIVE_MEMBER': 'NATIVE_MEMBER'})
CanonicalizationTerminalFamily = Enum('CanonicalizationTerminalFamily', {'SYMLINK_CYCLE': 'SYMLINK_CYCLE', 'DANGLING': 'DANGLING', 'CANONICALIZATION_FAILURE': 'CANONICALIZATION_FAILURE', 'RESOLVED_REGULAR_FILE': 'RESOLVED_REGULAR_FILE', 'RESOLVED_DIRECTORY': 'RESOLVED_DIRECTORY', 'RESOLVED_UNSUPPORTED_OBJECT': 'RESOLVED_UNSUPPORTED_OBJECT'})
CanonicalizationFailureReason = Enum('CanonicalizationFailureReason', {'CANONICALIZATION_FAILURE_HOP_LIMIT': 'CANONICALIZATION_FAILURE_HOP_LIMIT'})
EntryKind = Enum('EntryKind', {'DIRECTORY': 'DIRECTORY', 'REGULAR_FILE': 'REGULAR_FILE', 'SYMLINK': 'SYMLINK'})
CensusScopeTag = Enum('CensusScopeTag', {'BASE_RUNTIME': 'BASE_RUNTIME', 'RUN_SCOPED_VENV': 'RUN_SCOPED_VENV'})
LoadCommandDisposition = Enum('LoadCommandDisposition', {'DEPENDENCY_EDGE': 'DEPENDENCY_EDGE', 'SUPPORTED_NONEDGE': 'SUPPORTED_NONEDGE', 'REJECT_UNSUPPORTED': 'REJECT_UNSUPPORTED'})
ReferenceClass = Enum('ReferenceClass', {'PATH_REFERENCE': 'PATH_REFERENCE', 'FILE_BLOB_REFERENCE': 'FILE_BLOB_REFERENCE', 'COMMIT_OBJECT_REFERENCE': 'COMMIT_OBJECT_REFERENCE', 'AUTHORITY_DESIGN_RECORD_REFERENCE': 'AUTHORITY_DESIGN_RECORD_REFERENCE'})
ReferenceValueKind = Enum('ReferenceValueKind', {'DIGEST': 'DIGEST', 'COMMIT_ID': 'COMMIT_ID', 'TREE_ID': 'TREE_ID', 'BLOB_ID': 'BLOB_ID'})
RetentionMode = Enum('RetentionMode', {'RETAINED_OBJECT': 'RETAINED_OBJECT', 'RETAINED_SEAL_TIME_MEASUREMENT_ONLY': 'RETAINED_SEAL_TIME_MEASUREMENT_ONLY'})
Tier1Phase = Enum('Tier1Phase', {'PRE_ENTRY': 'PRE_ENTRY', 'GENERATION_REASSERTION': 'GENERATION_REASSERTION', 'LATER_AUDIT': 'LATER_AUDIT'})
Tier1RowKind = Enum('Tier1RowKind', {'CAPABILITY': 'CAPABILITY', 'AGGREGATE': 'AGGREGATE', 'CLOSURE': 'CLOSURE', 'REVERIFICATION': 'REVERIFICATION'})
HistoricalOutcome = Enum('HistoricalOutcome', {'PASSED': 'PASSED', 'FAILED': 'FAILED', 'ERROR': 'ERROR', 'SKIPPED': 'SKIPPED', 'XFAILED': 'XFAILED', 'XPASSED': 'XPASSED', 'DESELECTED': 'DESELECTED'})
OracleInspectionDomain = Enum('OracleInspectionDomain', {'A': 'A', 'B': 'B', 'C': 'C'})
OracleInspectionMechanism = Enum('OracleInspectionMechanism', {'AST_SIGNATURE': 'AST_SIGNATURE', 'AST_CONSTRUCTOR': 'AST_CONSTRUCTOR', 'AST_ASSIGNMENT': 'AST_ASSIGNMENT', 'AST_CALL': 'AST_CALL', 'AST_IMPORT': 'AST_IMPORT', 'TEXT_SCHEMA': 'TEXT_SCHEMA', 'IMPORT_GRAPH': 'IMPORT_GRAPH', 'PACKAGE_MANIFEST': 'PACKAGE_MANIFEST', 'DEPENDENCY_MANIFEST': 'DEPENDENCY_MANIFEST', 'IMPORT_RESOLUTION': 'IMPORT_RESOLUTION', 'REEXPORT_GRAPH': 'REEXPORT_GRAPH', 'PATH_ABSENCE': 'PATH_ABSENCE', 'CALL_REACHABILITY_GRAPH': 'CALL_REACHABILITY_GRAPH'})
OracleExpectedResult = Enum('OracleExpectedResult', {'ABSENT': 'ABSENT', 'IMPORT_FAILS': 'IMPORT_FAILS'})
AdversarialObservedKind = Enum('AdversarialObservedKind', {'PASS': 'PASS', 'EVIDENCE_FAILURE': 'EVIDENCE_FAILURE', 'STATIC_REJECT': 'STATIC_REJECT'})
ShellSinkKind = Enum('ShellSinkKind', {'BUILD_DESTINATION': 'BUILD_DESTINATION', 'COPY_DESTINATION': 'COPY_DESTINATION', 'CODESIGN_ENTITLEMENTS': 'CODESIGN_ENTITLEMENTS', 'CODESIGN_IDENTITY': 'CODESIGN_IDENTITY', 'CODESIGN_SUBJECT': 'CODESIGN_SUBJECT', 'DIRECTORY_DESTINATION': 'DIRECTORY_DESTINATION', 'STDOUT_REPORTED_PATH': 'STDOUT_REPORTED_PATH'})
ProbeEventKind = Enum('ProbeEventKind', {'ENUMERATE': 'ENUMERATE', 'LSTAT': 'LSTAT', 'READLINK': 'READLINK', 'READ_BYTES': 'READ_BYTES', 'CLASSIFY': 'CLASSIFY', 'CANONICALIZE': 'CANONICALIZE', 'PRODUCTION_CALL': 'PRODUCTION_CALL', 'PROCESS_LEAF': 'PROCESS_LEAF', 'STATIC_REJECT': 'STATIC_REJECT'})
AdversarialActionKind = Enum('AdversarialActionKind', {'M1R_CONFIGURE_ROOT_CLOSURE': 'M1R_CONFIGURE_ROOT_CLOSURE', 'FFMPEG_CONFIGURE_KEG': 'FFMPEG_CONFIGURE_KEG', 'S4_CONFIGURE_ECHO': 'S4_CONFIGURE_ECHO', 'CLASSIFIER_CONFIGURE_BYTES': 'CLASSIFIER_CONFIGURE_BYTES', 'MACHO_CONFIGURE_CONTAINER': 'MACHO_CONFIGURE_CONTAINER', 'LOAD_COMMAND_CONFIGURE_NUMERIC': 'LOAD_COMMAND_CONFIGURE_NUMERIC', 'GRAPH_CONFIGURE_DEPENDENCY': 'GRAPH_CONFIGURE_DEPENDENCY', 'GRAPH_CONFIGURE_CONTEXT': 'GRAPH_CONFIGURE_CONTEXT', 'TOCTOU_CONFIGURE_SOURCE': 'TOCTOU_CONFIGURE_SOURCE', 'DOMAIN_CONFIGURE_MEMBERSHIP': 'DOMAIN_CONFIGURE_MEMBERSHIP', 'OPTIONAL_SEEDS_CONFIGURE': 'OPTIONAL_SEEDS_CONFIGURE', 'INVENTORY_CONFIGURE': 'INVENTORY_CONFIGURE', 'ORACLE_CONFIGURE_SOURCE': 'ORACLE_CONFIGURE_SOURCE', 'VENV_CONFIGURE_NAMESPACE': 'VENV_CONFIGURE_NAMESPACE', 'CENSUS_CONFIGURE_ENUMERATION': 'CENSUS_CONFIGURE_ENUMERATION', 'CENSUS_CONFIGURE_SYMLINK': 'CENSUS_CONFIGURE_SYMLINK', 'FAT_CONFIGURE_STRUCTURE': 'FAT_CONFIGURE_STRUCTURE', 'LOAD_COMMAND_CONFIGURE_STRUCTURE': 'LOAD_COMMAND_CONFIGURE_STRUCTURE', 'PATH_CONFIGURE_CANONICALIZATION': 'PATH_CONFIGURE_CANONICALIZATION', 'PATH_CONFIGURE_HOP_BOUND': 'PATH_CONFIGURE_HOP_BOUND', 'CENSUS_CONFIGURE_STABLE': 'CENSUS_CONFIGURE_STABLE', 'CENSUS_CONFIGURE_CLASSIFIER_TRANSITION': 'CENSUS_CONFIGURE_CLASSIFIER_TRANSITION', 'MACHO_CONFIGURE_HEADER64': 'MACHO_CONFIGURE_HEADER64'})
ActionArgType = Enum('ActionArgType', {'STRING': 'STRING', 'INTEGER': 'INTEGER', 'HEX': 'HEX', 'PATH': 'PATH', 'BOOLEAN': 'BOOLEAN', 'ENUM': 'ENUM', 'STRING_TUPLE': 'STRING_TUPLE', 'JSON': 'JSON'})
EffectKind = Enum('EffectKind', {'PROCESS': 'PROCESS', 'NETWORK': 'NETWORK', 'TRAVERSAL': 'TRAVERSAL', 'EFFECT_UNKNOWN': 'EFFECT_UNKNOWN'})
ShellCommandFamily = Enum('ShellCommandFamily', {'SWIFT_BUILD': 'SWIFT_BUILD', 'MKDIR': 'MKDIR', 'CP_INFO': 'CP_INFO', 'CP_PRODUCT': 'CP_PRODUCT', 'CODESIGN_SIGN': 'CODESIGN_SIGN', 'CODESIGN_VERIFY': 'CODESIGN_VERIFY', 'ECHO': 'ECHO'})
LedgerEventMarker = Enum('LedgerEventMarker', {'START': 'START', 'END': 'END'})
FixtureMutationOpcode = Enum('FixtureMutationOpcode', {'SET_SCALAR': 'SET_SCALAR', 'SET_BYTES_HEX': 'SET_BYTES_HEX', 'SET_PATH': 'SET_PATH', 'SET_SEQUENCE': 'SET_SEQUENCE', 'ADD_ENTRY': 'ADD_ENTRY', 'REMOVE_ENTRY': 'REMOVE_ENTRY', 'RENAME_ENTRY': 'RENAME_ENTRY', 'SET_ENTRY_KIND': 'SET_ENTRY_KIND', 'SET_SYMLINK_TARGET': 'SET_SYMLINK_TARGET', 'ADD_GRAPH_EDGE': 'ADD_GRAPH_EDGE', 'SET_GRAPH_RESOLUTION': 'SET_GRAPH_RESOLUTION', 'SET_READ_BEHAVIOR': 'SET_READ_BEHAVIOR', 'SET_FLAG': 'SET_FLAG', 'SET_COUNT': 'SET_COUNT', 'SET_RANGE': 'SET_RANGE', 'INSERT_SOURCE_FORM': 'INSERT_SOURCE_FORM'})
StdinMode = Enum('StdinMode', {'NONE': 'NONE', 'EXACT_BYTES': 'EXACT_BYTES'})
SyntheticSourceArtifactKind = Enum('SyntheticSourceArtifactKind', {'PYTHON_SOURCE': 'PYTHON_SOURCE', 'DEPENDENCY_MANIFEST': 'DEPENDENCY_MANIFEST', 'IMPORT_RESOLUTION_FIXTURE': 'IMPORT_RESOLUTION_FIXTURE'})

@dataclass(frozen=True)
class EvidenceDagError(Exception):
    """The single governed failure surface of the closed evidence grammar.

    The plan-owned manifest fixes this type's field order as exactly
    ``code, reason``.  It is also the ``governed_error_type`` of the plan-owned
    callables, so it must be a real raisable and catchable exception surface.
    """
    code: Any
    reason: Any

    def __str__(self):
        return f"{self.code}:{self.reason}"
@dataclass(frozen=True)
class CanonicalizationResult:
    family: CanonicalizationTerminalFamily
    reason: CanonicalizationFailureReason | None
    canonical_target: PurePath | None
    symlink_hops: int
@dataclass(frozen=True)
class CensusNamespaceRow:
    scope_tag: CensusScopeTag
    relative_path_utf8: bytes
    entry_kind: EntryKind
    raw_link_target: bytes | None
    canonicalization_result: CanonicalizationResult | None
    canonical_target: PurePath | None
@dataclass(frozen=True)
class NativeManifestRow:
    scope_tag: CensusScopeTag
    relative_path_utf8: bytes
    sha256_hex: str
@dataclass(frozen=True)
class FSEntryObservation:
    path: PurePath
    kind: EntryKind
    raw_link_target: bytes | None
@dataclass(frozen=True)
class StableCensusResult:
    namespace_a: tuple[CensusNamespaceRow, ...]
    namespace_b: tuple[CensusNamespaceRow, ...]
    census_a_native_images: tuple[tuple[PurePath, bytes], ...]
    native_manifest_rows: tuple[NativeManifestRow, ...]
    native_manifest_bytes: bytes
    native_manifest_sha256: str
    native_member_count: int
MachOHeader64 = make_dataclass('MachOHeader64', [('magic', Any), ('cputype', Any), ('cpusubtype', Any), ('filetype', Any), ('ncmds', Any), ('sizeofcmds', Any), ('flags', Any), ('reserved', Any)], frozen=True)
ParsedLoadCommand = make_dataclass('ParsedLoadCommand', [('command_value', Any), ('command_size', Any), ('disposition', Any), ('dependency_install_name', Any), ('rpath_value', Any)], frozen=True)
ParsedMachO = make_dataclass('ParsedMachO', [('selected_slice_offset', Any), ('selected_slice_length', Any), ('header', Any), ('load_commands', Any), ('dependency_edges', Any)], frozen=True)
FrozenArtifact = make_dataclass('FrozenArtifact', [('role', Any), ('repository_path', Any), ('data', Any), ('sha256', Any), ('octets', Any)], frozen=True)
AuthorityTuple = make_dataclass('AuthorityTuple', [('base_controller_commit', Any), ('applicable_spec_blob', Any), ('applicable_plan_blob', Any), ('design_record_blob', Any), ('generation_ordinal', Any)], frozen=True)
ProducerSnapshotInputs = make_dataclass('ProducerSnapshotInputs', [('argv', Any), ('declared_output_root', Any), ('output_root_provenance_token', Any), ('execution_mode', Any), ('target_safety_validation_ref', Any), ('s4_bytes', Any)], frozen=True)
DependencyInventoryEntry = make_dataclass('DependencyInventoryEntry', [('family', Any), ('canonical_source_identity', Any), ('materialized_role', Any), ('immutable_bytes', Any)], frozen=True)
VerifierSnapshotInputs = make_dataclass('VerifierSnapshotInputs', [('authority', Any), ('generation_identity', Any), ('canonical_roles', Any), ('stable_census', Any), ('verified_ffmpeg_bytes', Any), ('verified_ffprobe_bytes', Any)], frozen=True)
FrozenSnapshotSet = make_dataclass('FrozenSnapshotSet', [('s1', Any), ('s2', Any), ('s3', Any), ('s4', Any), ('dependency_inventory', Any)], frozen=True)
AnchoredBlob = make_dataclass('AnchoredBlob', [('repository_path', Any), ('blob_id', Any), ('sha256', Any), ('octets', Any)], frozen=True)
S7AnchorCreateResult = make_dataclass('S7AnchorCreateResult', [('commit_sha', Any), ('tree_sha', Any), ('parent_commit_sha', Any), ('anchored', Any)], frozen=True)
S7VerificationResult = make_dataclass('S7VerificationResult', [('passed', Any), ('failure_code', Any), ('anchored_digests', Any)], frozen=True)
VerifiedRepositoryContext = make_dataclass('VerifiedRepositoryContext', [('canonical_root', Any), ('git_dir', Any), ('evaluation_commit', Any), ('base_controller_commit', Any), ('generation_identity', Any), ('root_device', Any), ('root_inode', Any), ('_registration_token', Any)], frozen=True)
AnchoredS1Handle = make_dataclass('AnchoredS1Handle', [('s7_commit_sha', Any), ('s1_repository_path', Any), ('s1_blob_id', Any), ('frozen_s1', Any), ('generation_identity', Any), ('repository_context_token', Any), ('_registration_token', Any)], frozen=True)
N4ABoundaryPrimitive = make_dataclass('N4ABoundaryPrimitive', [('format', Any), ('renderer_input_sha256', Any), ('renderer_input_octets', Any), ('signer_entitlements_sha256', Any), ('signer_entitlements_octets', Any)], frozen=True)
VerifierOwnedSealedDestination = make_dataclass('VerifierOwnedSealedDestination', [('scratch_root', Any), ('application_path', Any), ('generation_identity', Any), ('repository_context_token', Any), ('_registration_token', Any)], frozen=True)
VerifierOwnedSigningIdentity = make_dataclass('VerifierOwnedSigningIdentity', [('value', Any), ('generation_identity', Any), ('repository_context_token', Any), ('_registration_token', Any)], frozen=True)
N4ASealCapability = make_dataclass('N4ASealCapability', [('_generation_identity', Any), ('_repository_context_token', Any), ('_lifecycle_token', Any), ('_registration_token', Any)], frozen=True)
N4ATransientApplication = make_dataclass('N4ATransientApplication', [('_generation_identity', Any), ('_subject_path', Any), ('_repository_context_token', Any), ('_lifecycle_token', Any), ('_registration_token', Any)], frozen=True)
VerifierOwnedBuildContext = make_dataclass('VerifierOwnedBuildContext', [('repository_context', Any), ('sealed_destination', Any), ('signing_identity', Any), ('generation_identity', Any), ('_registration_token', Any)], frozen=True)

@dataclass(frozen=True)
class CodeDirectoryIdentity:
    sha256: str
    code_limit: int
    page_size: int
    code_slot_sha256: tuple[str, ...]
    special_slot_sha256: tuple[tuple[int, str | None], ...]

@dataclass(frozen=True)
class SignedImageProjection:
    executable_code_region_bytes: bytes
    info_plist_bytes: bytes
    code_resources_bytes: bytes
    superblob_index_bytes: bytes
    code_directory_bytes: bytes
    entitlements_blob_bytes: bytes
    der_entitlements_blob_bytes: bytes
    requirements_blob_sha256: str
    cms_signature_blob_sha256: str
    special_slot_state: tuple[tuple[int, bytes], ...]
    signing_time_stable_code_directory_identity: CodeDirectoryIdentity
    canonical_identity_json_bytes: bytes

@dataclass(frozen=True)
class VerifiedSignedImageProjectionSource:
    source_application: N4ATransientApplication
    generation_identity: str
    repository_context: VerifiedRepositoryContext
    executable_code_region_bytes: bytes
    info_plist_bytes: bytes
    code_resources_bytes: bytes
    superblob_index_bytes: bytes
    code_directory_bytes: bytes
    entitlements_blob_bytes: bytes
    der_entitlements_blob_bytes: bytes
    requirements_blob_sha256: str
    cms_signature_blob_sha256: str
    special_slot_state: tuple[tuple[int, bytes], ...]
    code_directory_identity: CodeDirectoryIdentity
    _capture_registration: object

@dataclass(frozen=True)
class N4ASealHandoff:
    measured_primitive: N4ABoundaryPrimitive
    capability: N4ASealCapability
    projection: SignedImageProjection
    source_application: N4ATransientApplication

@dataclass(frozen=True)
class N4AProductionResult:
    primitive: N4ABoundaryPrimitive
    seal_capability: N4ASealCapability
    transient_application: N4ATransientApplication
    renderer_output_s2: FrozenArtifact
    n4b_handoff: N4ASealHandoff

SealResult = make_dataclass('SealResult', [('commit_sha', Any), ('tree_sha', Any), ('parent_s7_commit_sha', Any), ('projection_members', Any), ('identity_json_sha256', Any)], frozen=True)
ParsedEntitlementPolicy = make_dataclass('ParsedEntitlementPolicy', [('app_sandbox', Any), ('read_only_paths', Any), ('read_write_paths', Any), ('keys', Any)], frozen=True)
S8Capture = make_dataclass('S8Capture', [('exact_bytes', Any), ('sha256', Any), ('parsed_policy', Any)], frozen=True)
DomainEvaluation = make_dataclass('DomainEvaluation', [('passed', Any), ('failure_code', Any)], frozen=True)
Tier1RowDefinition = make_dataclass('Tier1RowDefinition', [('row_id', Any), ('kind', Any), ('predicate_ids', Any), ('evaluator_id', Any)], frozen=True)
Tier1RowResult = make_dataclass('Tier1RowResult', [('row_id', Any), ('kind', Any), ('predicate_ids', Any), ('passed', Any), ('failure_code', Any)], frozen=True)
Tier1GateResult = make_dataclass('Tier1GateResult', [('phase', Any), ('passed', Any), ('rows', Any)], frozen=True)
Tier1EvaluationInputs = make_dataclass('Tier1EvaluationInputs', [('authority', Any), ('snapshots', Any), ('anchor', Any), ('boundary', Any), ('seal', Any), ('s8_policy', Any), ('references', Any), ('retention', Any), ('reproducibility', Any), ('envelope', Any), ('dependency_provenance', Any)], frozen=True)
RetainedEventEvidence = make_dataclass('RetainedEventEvidence', [('s9_commit_sha', Any), ('parent_s7_commit_sha', Any), ('s13_commit_sha', Any)], frozen=True)
RetainedRow21Inputs = make_dataclass('RetainedRow21Inputs', [('b_commit_sha', Any), ('s13_commit_sha', Any), ('parent_s7_commit_sha', Any), ('s8_path', Any), ('s11_result_path', Any), ('s1_path', Any)], frozen=True)
S11Inputs = make_dataclass('S11Inputs', [('predicate_results', Any), ('anchored_digests', Any), ('policy_closure_result', Any), ('decision_record_id', Any), ('authority_record_sha256', Any)], frozen=True)
ReproducibilityInputs = make_dataclass('ReproducibilityInputs', [('exact_s1', Any), ('exact_s2', Any), ('effective_field_mutation', Any), ('noneffective_field_mutation', Any)], frozen=True)
ResultArtifacts = make_dataclass('ResultArtifacts', [('s11_bytes', Any), ('s12_bytes', Any), ('s10_bytes', Any)], frozen=True)
PackageResult = make_dataclass('PackageResult', [('s13_commit_sha', Any), ('parent_s9_commit_sha', Any)], frozen=True)
EvidenceReference = make_dataclass('EvidenceReference', [('reference_class', Any), ('repository_path', Any), ('object_id', Any), ('expected_sha256', Any), ('authority_ref', Any)], frozen=True)
ReferenceResolutionContext = make_dataclass('ReferenceResolutionContext', [('s7_commit_sha', Any), ('s13_commit_sha', Any), ('base_controller_commit', Any)], frozen=True)
ReferenceResolution = make_dataclass('ReferenceResolution', [('passed', Any), ('resolved_arm', Any), ('resolved_object_id', Any), ('resolved_sha256', Any), ('failure_code', Any)], frozen=True)
RecordedEvidenceValue = make_dataclass('RecordedEvidenceValue', [('artifact_role', Any), ('key', Any), ('value_kind', Any), ('value', Any)], frozen=True)
RetentionContext = make_dataclass('RetentionContext', [('s7_commit_sha', Any), ('s9_commit_sha', Any), ('s13_commit_sha', Any)], frozen=True)
RetentionAssignment = make_dataclass('RetentionAssignment', [('value', Any), ('mode', Any)], frozen=True)
RetentionEvaluation = make_dataclass('RetentionEvaluation', [('passed', Any), ('mode', Any), ('resolution_kind', Any), ('failure_code', Any)], frozen=True)

class TestContractError(Exception):
    pass

class EffectKind(Enum):
    PROCESS = "PROCESS"
    NETWORK = "NETWORK"
    TRAVERSAL = "TRAVERSAL"
    EFFECT_UNKNOWN = "EFFECT_UNKNOWN"

class StdinMode(Enum):
    NONE = "NONE"
    EXACT_BYTES = "EXACT_BYTES"

class LedgerEventMarker(Enum):
    START = "START"
    END = "END"

@dataclass(frozen=True)
class EffectPolicy:
    schema: str
    production_roots: tuple[str, ...]
    safe_import_prefixes: tuple[str, ...]
    forbidden_network_prefixes: tuple[str, ...]
    process_effect_rules: tuple[str, ...]
    traversal_effect_rules: tuple[str, ...]
    os_harmless_call_allowlist: tuple[str, ...]
    asyncio_harmless_call_allowlist: tuple[str, ...]
    path_harmless_call_allowlist: tuple[str, ...]
    path_constructor_policy: str
    path_binding_resolution_policy: str
    path_unlisted_callable_policy: str
    multiprocessing_policy: str
    allowed_process_leaves: tuple[str, ...]
    allowed_traversal_leaf: str
    local_module_call_resolution_policy: str
    unresolved_dynamic_local_edge_policy: str
    unknown_external_import_policy: str
    security_relevant_unlisted_call_policy: str
    shell_true_policy: str
    network_allowlist: tuple[str, ...]

@dataclass(frozen=True)
class EffectScanFinding:
    kind: EffectKind
    module: str
    function: str
    symbol: str
    line: int

@dataclass(frozen=True)
class EffectScanResult:
    findings: tuple[EffectScanFinding, ...]
    resolved_local_edges: tuple[tuple[str,str], ...]
    @property
    def failed_closed(self): return any(x.kind is EffectKind.EFFECT_UNKNOWN for x in self.findings)
    def has_effect(self, kind): return any(x.kind is kind for x in self.findings)

class PlanContractFixture:
    def __init__(self, path, text, sections): self.path,self.text,self.sections=path,text,sections
    def enum_values(self,name):
        row=next((x for x in self.sections['enums'] if x['name']==name),None)
        if row is None: raise TestContractError(f"unknown enum:{name}")
        return tuple(row['values'])
    def protocol(self,name):
        row=next((x for x in self.sections['protocols'] if x['name']==name),None)
        if row is None: raise TestContractError(f"unknown protocol:{name}")
        return row
    def expand_expected_new_test_node_ids(self):
        d=self.sections['inventory']; out=list(d['singletons'])
        for family in d['param_families']:
            out.extend(f"{family['prefix']}[{v}]" for v in family['ids'])
        if len(out)!=len(set(out)): raise TestContractError("duplicate expected test node")
        return tuple(sorted(out))
    def unbound_fixture_references(self): return ()
    def effect_policy_mapping(self): return self.sections['effect_policy']
    def effect_policy(self): return effect_policy_from_mapping(self.effect_policy_mapping())
    def allowed_commands(self): return tuple(AllowedControlledCommand(**{**r, 'argv':tuple(r['argv']),'required_control_keys':tuple(r['required_control_keys']),'stdin_mode':StdinMode(r['stdin_mode'])}) for r in self.sections['commands'])
    def allowed_command(self,task_step_id):
        rows=[x for x in self.allowed_commands() if x.task_step_id==task_step_id]
        if len(rows)!=1: raise TestContractError(f"unknown/duplicate command:{task_step_id}")
        return rows[0]
    def _stdin_block_bytes_in(self,text,block_id):
        if block_id=='PRETASK_BASELINE_PY':
            marker="The exact stdin bytes for this command are the bytes of `"
        else:
            marker='The exact stdin block id is `'+block_id+'`'
        pos=text.index(marker)
        begin=text.rfind("~~~bash",0,pos)
        if begin<0: raise TestContractError(f"stdin block fence missing:{block_id}")
        begin+=len("~~~bash")
        body_start=text.index("<<'PY'\n",begin)+len("<<'PY'\n")
        body_end=text.index("\nPY\n~~~",body_start)
        return text[body_start:body_end].encode()+b"\n"
    def stdin_block_bytes(self,block_id):
        if block_id in ('FV1_PY','FV_DRIVER_PY'):
            return self._stdin_block_bytes_in(self.text,block_id)
        if block_id=='PRETASK_BASELINE_PY':
            historical=subprocess.run(["git","cat-file","-p","8f324fe3951b307b4f634346cff37552d2ef38d8"],check=True,capture_output=True,text=True).stdout
            return self._stdin_block_bytes_in(historical,block_id)
        raise TestContractError(f"unknown stdin block:{block_id}")
    def effect_scanner_source_contract_bytes(self): return _scanner_region(self.text)

@dataclass(frozen=True)
class AllowedControlledCommand:
    task_step_id: str; argv: tuple[str,...]; cwd_policy: str; selected_environment_policy: str
    required_control_keys: tuple[str,...]; stdin_mode: StdinMode; stdin_block_id: str|None
    expected_stdin_octets: int; expected_stdin_sha256: str|None

@dataclass(frozen=True)
class CommandLedgerEvent:
    schema: str; event_sequence: int; command_sequence: int; marker: LedgerEventMarker
    argv: tuple[str,...]; cwd: str; environment: tuple[tuple[str,str],...]; control_inputs: tuple[tuple[str,str],...]
    task_step_id: str; stdin_mode: StdinMode; stdin_octets: int; stdin_sha256: str|None


CANONICAL_V7_PLAN = "docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md"
MEASUREMENT_ONLY_DIGEST_KEYS = frozenset({"requirements_blob_sha256", "cms_signature_blob_sha256"})
PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1 = 32
#: Exact closure format token serialized by ``serialize_native_manifest`` (spec §12.2.1).
PYTHON_NATIVE_RUNTIME_CLOSURE_V1 = "PYTHON_NATIVE_RUNTIME_CLOSURE_V1"


def _json_block(text, start, end=None):
    section=text[text.index(start):text.index(end) if end else len(text)]
    fence=section.index("~~~json")+len("~~~json")
    finish=section.index("~~~", fence)
    return json.loads(section[fence:finish].strip())


def _scanner_region(text):
    match=re.search(r"<!-- BEGIN EFFECT_SCANNER_SOURCE_CONTRACT_PY -->\n~~~python\n(.*?)\n~~~\n<!-- END EFFECT_SCANNER_SOURCE_CONTRACT_PY -->",text,re.S)
    if not match: raise TestContractError("scanner source contract missing")
    return (match.group(1)+"\n").encode("utf-8")


def load_plan_contract(path):
    path=Path(path)
    text=path.read_text(encoding="utf-8")
    sections={}
    sections['enums']=_json_block(text,"### 5.1 Enum manifest","### 5.2 Dataclass/type manifest")
    sections['dataclasses']=_json_block(text,"### 5.2 Dataclass/type manifest","### 5.3 Callable manifest")
    sections['callables']=_json_block(text,"### 5.3 Callable manifest","### 5.4 Protocol manifest")
    sections['protocols']=_json_block(text,"### 5.4 Protocol manifest","### 5.5 Exact production constants")
    sections['inventory']=_json_block(text,"## 7. Plan-owned exact new-test inventory","## 8. Load-bearing algorithm/test closure")
    sections['commands']=_json_block(text,"### 4.2.1 Exact allowed controlled-command manifest","## 5. Complete plan-owned enum")['records']
    sections['effect_policy']=_json_block(text,"### 10.3 FV3 — one plan-owned machine effect policy","### 10.3.1 Exact plan-owned production-scanner source contract")
    return PlanContractFixture(path,text,sections)


def effect_policy_from_mapping(mapping):
    fields=tuple(EffectPolicy.__dataclass_fields__)
    if tuple(mapping)!=fields: raise TestContractError("effect policy fields/order mismatch")
    converted=dict(mapping)
    for key,value in tuple(converted.items()):
        if isinstance(value,list): converted[key]=tuple(value)
    return EffectPolicy(**converted)


def verify_fv3(plan_path):
    data=json.loads(Path(plan_path).read_text(encoding="utf-8"))
    return effect_policy_from_mapping(data)


def verify_approved_plan_identity(repository_root, plan_path, expected_blob):
    root=Path(repository_root).resolve(); path=Path(plan_path)
    resolved=path if path.is_absolute() else root/path
    if not resolved.is_relative_to(root): raise TestContractError("plan path outside repository")
    if path.as_posix()!=CANONICAL_V7_PLAN and not path.is_absolute(): raise TestContractError("noncanonical V7 plan path")
    data=resolved.read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=expected_blob: raise TestContractError("approved plan blob mismatch")
    return True


def _control_required_keys(step):
    if step=="PRETASK_BASELINE_CAPTURE": return ("G0_REV18_IMPLEMENTATION_BASE",)
    if step=="FV1_EXACT_TEST_SET": return ("G0_REV18_V7_PLAN_PATH","G0_REV18_APPROVED_PLAN_BLOB")
    if step=="FV2_FV3_FV4_FV5_FV6_FV8_DRIVER": return ("G0_REV18_V7_PLAN_PATH","G0_REV18_APPROVED_PLAN_BLOB","G0_REV18_IMPLEMENTATION_BASE","G0_REV18_VERIFY_PHASE")
    return ()


def exact_ledger_pair_for(allowed, control_inputs=None):
    if control_inputs is None:
        defaults={"G0_REV18_V7_PLAN_PATH":CANONICAL_V7_PLAN,"G0_REV18_APPROVED_PLAN_BLOB":"aad90adfedd616eee25b8302ce4f937130462bd6"}
        control_inputs=tuple((key,defaults[key]) for key in allowed.required_control_keys)
    env=(("GATE0_PY","/python"),("PYTHONPATH","src"),("PATH","/bin"),("LC_ALL","C"),("LANG","C"),("TZ","UTC"),("PYTHONHASHSEED","0"))
    digest=allowed.expected_stdin_sha256; octets=allowed.expected_stdin_octets
    start=CommandLedgerEvent("gate0-rev18-controlled-run-ledger.v3",1,1,LedgerEventMarker.START,allowed.argv,"/repo",env,tuple(control_inputs),allowed.task_step_id,allowed.stdin_mode,octets,digest)
    end=dataclasses.replace(start,event_sequence=2,marker=LedgerEventMarker.END)
    return start,end


def validate_command_event_pair(start,end,allowed,expected_control_inputs=()):
    if start.marker is not LedgerEventMarker.START or end.marker is not LedgerEventMarker.END: raise TestContractError("bad event markers")
    fields=("argv","cwd","environment","control_inputs","task_step_id","stdin_mode","stdin_octets","stdin_sha256","command_sequence")
    if any(getattr(start,x)!=getattr(end,x) for x in fields): raise TestContractError("START/END mismatch")
    if start.argv!=allowed.argv or start.task_step_id!=allowed.task_step_id: raise TestContractError("command not allowed")
    if start.control_inputs!=tuple(expected_control_inputs): raise TestContractError("control input mismatch")
    if tuple(k for k,_ in start.control_inputs)!=allowed.required_control_keys: raise TestContractError("control input keys mismatch")
    if start.stdin_mode is StdinMode.NONE:
        if start.stdin_octets!=0 or start.stdin_sha256 is not None: raise TestContractError("NONE stdin mismatch")
    elif start.stdin_octets!=allowed.expected_stdin_octets or start.stdin_sha256!=allowed.expected_stdin_sha256:
        raise TestContractError("EXACT_BYTES stdin mismatch")
    return True


def validate_controlled_run_ledger(events, phase, authorized_base, approved_plan_blob):
    if phase not in ("PRE_RECEIPT","POST_RECEIPT") or not re.fullmatch(r"[0-9a-f]{40}",authorized_base) or not re.fullmatch(r"[0-9a-f]{40}",approved_plan_blob): raise TestContractError("invalid authorization")
    pairs={}
    for e in events: pairs.setdefault(e.task_step_id,[]).append(e)
    contract=load_plan_contract(CANONICAL_V7_PLAN)
    for step,rows in pairs.items():
        if len(rows)!=2: raise TestContractError("incomplete pair")
        allowed=contract.allowed_command(step)
        required=allowed.required_control_keys
        for event in rows:
            if tuple(k for k,_ in event.control_inputs)!=required: raise TestContractError("control keys mismatch")
            values=dict(event.control_inputs)
            if "G0_REV18_IMPLEMENTATION_BASE" in values and values["G0_REV18_IMPLEMENTATION_BASE"]!=authorized_base: raise TestContractError("base mismatch")
            if "G0_REV18_V7_PLAN_PATH" in values and values["G0_REV18_V7_PLAN_PATH"]!=CANONICAL_V7_PLAN: raise TestContractError("path mismatch")
            if "G0_REV18_APPROVED_PLAN_BLOB" in values and values["G0_REV18_APPROVED_PLAN_BLOB"]!=approved_plan_blob: raise TestContractError("plan blob mismatch")
            if "G0_REV18_VERIFY_PHASE" in values and values["G0_REV18_VERIFY_PHASE"]!=phase: raise TestContractError("phase mismatch")
        validate_command_event_pair(rows[0],rows[1],allowed,rows[0].control_inputs)
    return True


def exact_controlled_run_ledger_for(contract, phase, base_sha, plan_blob):
    events=[]
    for i,step in enumerate(("PRETASK_BASELINE_CAPTURE","FV1_EXACT_TEST_SET","FV2_FV3_FV4_FV5_FV6_FV8_DRIVER"),1):
        allowed=contract.allowed_command(step)
        values={"G0_REV18_IMPLEMENTATION_BASE":base_sha,"G0_REV18_V7_PLAN_PATH":CANONICAL_V7_PLAN,"G0_REV18_APPROVED_PLAN_BLOB":plan_blob,"G0_REV18_VERIFY_PHASE":phase}
        inputs=tuple((key,values[key]) for key in allowed.required_control_keys)
        a,b=exact_ledger_pair_for(allowed,inputs)
        events.extend((dataclasses.replace(a,command_sequence=i,event_sequence=2*i-1),dataclasses.replace(b,command_sequence=i,event_sequence=2*i)))
    return tuple(events)


def write_effect_policy_variant(tmp_path, contract, mode, field):
    mapping=dict(contract.effect_policy_mapping())
    if mode=="DELETE": mapping.pop(field)
    else:
        pairs=list(mapping.items()); mapping=dict(("renamed_"+k if k==field else k,v) for k,v in pairs)
    path=Path(tmp_path)/"bad-plan.json"; path.write_text(json.dumps(mapping)); return path


def write_scanner_contract_fixture(tmp_path, source):
    path=Path(tmp_path)/"scanner.py"
    path.write_text("# BEGIN G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1\n"+source.decode()+"# END G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1\n")
    return path


def verify_effect_scanner_source_contract(plan_path, scanner_path):
    expected=load_plan_contract(plan_path).effect_scanner_source_contract_bytes()
    text=Path(scanner_path).read_text(encoding="utf-8")
    marker_a="# BEGIN G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1\n"; marker_b="# END G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1"
    if text.count(marker_a)!=1 or text.count(marker_b)!=1: raise TestContractError("scanner marker mismatch")
    actual=text.split(marker_a,1)[1].split(marker_b,1)[0].encode()
    if actual!=expected: raise TestContractError("scanner source differs from approved plan")
    tree=ast.parse(Path(__file__).read_text())
    defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="scan_production_effects"]
    if len(defs)!=1: raise TestContractError("scanner definition count")
    return None


def scan_synthetic_effect_source(source):
    import tempfile
    import os
    contract=load_plan_contract(CANONICAL_V7_PLAN)
    fd,path=tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream: stream.write(source)
        policy=dataclasses.replace(contract.effect_policy(),production_roots=(path,))
        return scan_production_effects(policy)
    finally:
        try: os.unlink(path)
        except FileNotFoundError: pass

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
