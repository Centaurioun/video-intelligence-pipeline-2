"""Plan-owned V7 interface truth copied from approved plan blob aad90adf.

Do not edit this manifest to match implementation output.
"""
import json

INTERFACE_MANIFEST = json.loads(r'''{
  "enums": [
    {
      "name": "EvidenceFailureCode",
      "values": [
        "AUTHORITY_ECHO_MISMATCH",
        "AUTHORITY_CONSUMPTION_NOT_RECORDED",
        "GENERATION_IDENTITY_COLLISION",
        "RENDER_INPUT_NOT_FROZEN",
        "OUTPUT_ROOT_AMBIGUOUS",
        "PREBUILD_ANCHOR_NOT_FROZEN",
        "FROZEN_EVIDENCE_MUTATED_BY_BUILD",
        "ANCHOR_DIGEST_NOT_RECORDED",
        "BUILD_OUTPUT_SEAL_NOT_FROZEN",
        "SEAL_IDENTITY_HOME_INCOMPLETE",
        "SIGNING_ENTITLEMENTS_NOT_FROZEN",
        "SIGNING_IDENTITY_DRIFT",
        "SIGNED_BYTES_NOT_VERIFIER_DERIVED",
        "ENTITLEMENT_ALLOWLIST_VIOLATION",
        "ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE",
        "S8_NOT_RETAINED_EXACTLY",
        "POLICY_CLOSURE_RESULT_NOT_RECORDED",
        "SEAL_PROJECTION_ELISION_INVALID",
        "SEAL_PROJECTION_PRIVACY_VIOLATION",
        "RENDER_NOT_BYTE_REPRODUCIBLE",
        "REPRODUCIBILITY_PROOF_VACUOUS",
        "RESULT_MANIFEST_NOT_FINAL",
        "EVIDENCE_PACKAGE_NOT_ADDITIVE",
        "EVIDENCE_NOT_RETAINED",
        "EVIDENCE_REFERENCE_UNRESOLVED",
        "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
        "GENERATION_B_TIER1_GATE_UNMET",
        "GATE_COVERAGE_INCOMPLETE",
        "ENVELOPE_REFERENCE_NOT_ACCEPTED"
      ]
    },
    {
      "name": "NativeCandidateClassification",
      "values": [
        "NON_NATIVE",
        "UNSUPPORTED_MACHO_CANDIDATE",
        "NATIVE_MEMBER"
      ]
    },
    {
      "name": "CanonicalizationTerminalFamily",
      "values": [
        "SYMLINK_CYCLE",
        "DANGLING",
        "CANONICALIZATION_FAILURE",
        "RESOLVED_REGULAR_FILE",
        "RESOLVED_DIRECTORY",
        "RESOLVED_UNSUPPORTED_OBJECT"
      ]
    },
    {
      "name": "CanonicalizationFailureReason",
      "values": [
        "CANONICALIZATION_FAILURE_HOP_LIMIT"
      ]
    },
    {
      "name": "EntryKind",
      "values": [
        "DIRECTORY",
        "REGULAR_FILE",
        "SYMLINK"
      ]
    },
    {
      "name": "CensusScopeTag",
      "values": [
        "BASE_RUNTIME",
        "RUN_SCOPED_VENV"
      ]
    },
    {
      "name": "LoadCommandDisposition",
      "values": [
        "DEPENDENCY_EDGE",
        "SUPPORTED_NONEDGE",
        "REJECT_UNSUPPORTED"
      ]
    },
    {
      "name": "ReferenceClass",
      "values": [
        "PATH_REFERENCE",
        "FILE_BLOB_REFERENCE",
        "COMMIT_OBJECT_REFERENCE",
        "AUTHORITY_DESIGN_RECORD_REFERENCE"
      ]
    },
    {
      "name": "ReferenceValueKind",
      "values": [
        "DIGEST",
        "COMMIT_ID",
        "TREE_ID",
        "BLOB_ID"
      ]
    },
    {
      "name": "RetentionMode",
      "values": [
        "RETAINED_OBJECT",
        "RETAINED_SEAL_TIME_MEASUREMENT_ONLY"
      ]
    },
    {
      "name": "Tier1Phase",
      "values": [
        "PRE_ENTRY",
        "GENERATION_REASSERTION",
        "LATER_AUDIT"
      ]
    },
    {
      "name": "Tier1RowKind",
      "values": [
        "CAPABILITY",
        "AGGREGATE",
        "CLOSURE",
        "REVERIFICATION"
      ]
    },
    {
      "name": "HistoricalOutcome",
      "values": [
        "PASSED",
        "FAILED",
        "ERROR",
        "SKIPPED",
        "XFAILED",
        "XPASSED",
        "DESELECTED"
      ]
    },
    {
      "name": "OracleInspectionDomain",
      "values": [
        "A",
        "B",
        "C"
      ]
    },
    {
      "name": "OracleInspectionMechanism",
      "values": [
        "AST_SIGNATURE",
        "AST_CONSTRUCTOR",
        "AST_ASSIGNMENT",
        "AST_CALL",
        "AST_IMPORT",
        "TEXT_SCHEMA",
        "IMPORT_GRAPH",
        "PACKAGE_MANIFEST",
        "DEPENDENCY_MANIFEST",
        "IMPORT_RESOLUTION",
        "REEXPORT_GRAPH",
        "PATH_ABSENCE",
        "CALL_REACHABILITY_GRAPH"
      ]
    },
    {
      "name": "OracleExpectedResult",
      "values": [
        "ABSENT",
        "IMPORT_FAILS"
      ]
    },
    {
      "name": "AdversarialObservedKind",
      "values": [
        "PASS",
        "EVIDENCE_FAILURE",
        "STATIC_REJECT"
      ]
    },
    {
      "name": "ShellSinkKind",
      "values": [
        "BUILD_DESTINATION",
        "COPY_DESTINATION",
        "CODESIGN_ENTITLEMENTS",
        "CODESIGN_IDENTITY",
        "CODESIGN_SUBJECT",
        "DIRECTORY_DESTINATION",
        "STDOUT_REPORTED_PATH"
      ]
    },
    {
      "name": "ProbeEventKind",
      "values": [
        "ENUMERATE",
        "LSTAT",
        "READLINK",
        "READ_BYTES",
        "CLASSIFY",
        "CANONICALIZE",
        "PRODUCTION_CALL",
        "PROCESS_LEAF",
        "STATIC_REJECT"
      ]
    },
    {
      "name": "AdversarialActionKind",
      "values": [
        "M1R_CONFIGURE_ROOT_CLOSURE",
        "FFMPEG_CONFIGURE_KEG",
        "S4_CONFIGURE_ECHO",
        "CLASSIFIER_CONFIGURE_BYTES",
        "MACHO_CONFIGURE_CONTAINER",
        "LOAD_COMMAND_CONFIGURE_NUMERIC",
        "GRAPH_CONFIGURE_DEPENDENCY",
        "GRAPH_CONFIGURE_CONTEXT",
        "TOCTOU_CONFIGURE_SOURCE",
        "DOMAIN_CONFIGURE_MEMBERSHIP",
        "OPTIONAL_SEEDS_CONFIGURE",
        "INVENTORY_CONFIGURE",
        "ORACLE_CONFIGURE_SOURCE",
        "VENV_CONFIGURE_NAMESPACE",
        "CENSUS_CONFIGURE_ENUMERATION",
        "CENSUS_CONFIGURE_SYMLINK",
        "FAT_CONFIGURE_STRUCTURE",
        "LOAD_COMMAND_CONFIGURE_STRUCTURE",
        "PATH_CONFIGURE_CANONICALIZATION",
        "PATH_CONFIGURE_HOP_BOUND",
        "CENSUS_CONFIGURE_STABLE",
        "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
        "MACHO_CONFIGURE_HEADER64"
      ]
    },
    {
      "name": "ActionArgType",
      "values": [
        "STRING",
        "INTEGER",
        "HEX",
        "PATH",
        "BOOLEAN",
        "ENUM",
        "STRING_TUPLE",
        "JSON"
      ]
    },
    {
      "name": "EffectKind",
      "values": [
        "PROCESS",
        "NETWORK",
        "TRAVERSAL",
        "EFFECT_UNKNOWN"
      ]
    },
    {
      "name": "ShellCommandFamily",
      "values": [
        "SWIFT_BUILD",
        "MKDIR",
        "CP_INFO",
        "CP_PRODUCT",
        "CODESIGN_SIGN",
        "CODESIGN_VERIFY",
        "ECHO"
      ]
    },
    {
      "name": "LedgerEventMarker",
      "values": [
        "START",
        "END"
      ]
    },
    {
      "name": "FixtureMutationOpcode",
      "values": [
        "SET_SCALAR",
        "SET_BYTES_HEX",
        "SET_PATH",
        "SET_SEQUENCE",
        "ADD_ENTRY",
        "REMOVE_ENTRY",
        "RENAME_ENTRY",
        "SET_ENTRY_KIND",
        "SET_SYMLINK_TARGET",
        "ADD_GRAPH_EDGE",
        "SET_GRAPH_RESOLUTION",
        "SET_READ_BEHAVIOR",
        "SET_FLAG",
        "SET_COUNT",
        "SET_RANGE",
        "INSERT_SOURCE_FORM"
      ]
    },
    {
      "name": "StdinMode",
      "values": [
        "NONE",
        "EXACT_BYTES"
      ]
    },
    {
      "name": "SyntheticSourceArtifactKind",
      "values": [
        "PYTHON_SOURCE",
        "DEPENDENCY_MANIFEST",
        "IMPORT_RESOLUTION_FIXTURE"
      ]
    }
  ],
  "dataclasses": [
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "EvidenceDagError",
      "fields": [
        {
          "name": "code",
          "type": "EvidenceFailureCode"
        },
        {
          "name": "reason",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "CanonicalizationResult",
      "fields": [
        {
          "name": "family",
          "type": "CanonicalizationTerminalFamily"
        },
        {
          "name": "reason",
          "type": "CanonicalizationFailureReason | None"
        },
        {
          "name": "canonical_target",
          "type": "PurePath | None"
        },
        {
          "name": "symlink_hops",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "CensusNamespaceRow",
      "fields": [
        {
          "name": "scope_tag",
          "type": "CensusScopeTag"
        },
        {
          "name": "relative_path_utf8",
          "type": "bytes"
        },
        {
          "name": "entry_kind",
          "type": "EntryKind"
        },
        {
          "name": "raw_link_target",
          "type": "bytes | None"
        },
        {
          "name": "canonicalization_result",
          "type": "CanonicalizationResult | None"
        },
        {
          "name": "canonical_target",
          "type": "PurePath | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "NativeManifestRow",
      "fields": [
        {
          "name": "scope_tag",
          "type": "CensusScopeTag"
        },
        {
          "name": "relative_path_utf8",
          "type": "bytes"
        },
        {
          "name": "sha256_hex",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "FSEntryObservation",
      "fields": [
        {
          "name": "path",
          "type": "PurePath"
        },
        {
          "name": "kind",
          "type": "EntryKind"
        },
        {
          "name": "raw_link_target",
          "type": "bytes | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "StableCensusResult",
      "fields": [
        {
          "name": "namespace_a",
          "type": "tuple[CensusNamespaceRow, ...]"
        },
        {
          "name": "namespace_b",
          "type": "tuple[CensusNamespaceRow, ...]"
        },
        {
          "name": "census_a_native_images",
          "type": "tuple[tuple[PurePath, bytes], ...]"
        },
        {
          "name": "native_manifest_rows",
          "type": "tuple[NativeManifestRow, ...]"
        },
        {
          "name": "native_manifest_bytes",
          "type": "bytes"
        },
        {
          "name": "native_manifest_sha256",
          "type": "str"
        },
        {
          "name": "native_member_count",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "MachOHeader64",
      "fields": [
        {
          "name": "magic",
          "type": "int"
        },
        {
          "name": "cputype",
          "type": "int"
        },
        {
          "name": "cpusubtype",
          "type": "int"
        },
        {
          "name": "filetype",
          "type": "int"
        },
        {
          "name": "ncmds",
          "type": "int"
        },
        {
          "name": "sizeofcmds",
          "type": "int"
        },
        {
          "name": "flags",
          "type": "int"
        },
        {
          "name": "reserved",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ParsedLoadCommand",
      "fields": [
        {
          "name": "command_value",
          "type": "int"
        },
        {
          "name": "command_size",
          "type": "int"
        },
        {
          "name": "disposition",
          "type": "LoadCommandDisposition"
        },
        {
          "name": "dependency_install_name",
          "type": "bytes | None"
        },
        {
          "name": "rpath_value",
          "type": "bytes | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ParsedMachO",
      "fields": [
        {
          "name": "selected_slice_offset",
          "type": "int"
        },
        {
          "name": "selected_slice_length",
          "type": "int"
        },
        {
          "name": "header",
          "type": "MachOHeader64"
        },
        {
          "name": "load_commands",
          "type": "tuple[ParsedLoadCommand, ...]"
        },
        {
          "name": "dependency_edges",
          "type": "tuple[bytes, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "FrozenArtifact",
      "fields": [
        {
          "name": "role",
          "type": "Literal['S1','S2','S3','S4']"
        },
        {
          "name": "repository_path",
          "type": "str"
        },
        {
          "name": "data",
          "type": "bytes"
        },
        {
          "name": "sha256",
          "type": "str"
        },
        {
          "name": "octets",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "AuthorityTuple",
      "fields": [
        {
          "name": "base_controller_commit",
          "type": "str"
        },
        {
          "name": "applicable_spec_blob",
          "type": "str"
        },
        {
          "name": "applicable_plan_blob",
          "type": "str"
        },
        {
          "name": "design_record_blob",
          "type": "str"
        },
        {
          "name": "generation_ordinal",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ProducerSnapshotInputs",
      "fields": [
        {
          "name": "argv",
          "type": "tuple[str, ...]"
        },
        {
          "name": "declared_output_root",
          "type": "str"
        },
        {
          "name": "output_root_provenance_token",
          "type": "str"
        },
        {
          "name": "execution_mode",
          "type": "str"
        },
        {
          "name": "target_safety_validation_ref",
          "type": "str"
        },
        {
          "name": "s4_bytes",
          "type": "bytes"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "DependencyInventoryEntry",
      "fields": [
        {
          "name": "family",
          "type": "Literal['PYTHON','TOOL']"
        },
        {
          "name": "canonical_source_identity",
          "type": "str"
        },
        {
          "name": "materialized_role",
          "type": "str"
        },
        {
          "name": "immutable_bytes",
          "type": "bytes"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "VerifierSnapshotInputs",
      "fields": [
        {
          "name": "authority",
          "type": "AuthorityTuple"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "canonical_roles",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "stable_census",
          "type": "StableCensusResult"
        },
        {
          "name": "verified_ffmpeg_bytes",
          "type": "bytes"
        },
        {
          "name": "verified_ffprobe_bytes",
          "type": "bytes"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "FrozenSnapshotSet",
      "fields": [
        {
          "name": "s1",
          "type": "FrozenArtifact"
        },
        {
          "name": "s2",
          "type": "FrozenArtifact"
        },
        {
          "name": "s3",
          "type": "FrozenArtifact"
        },
        {
          "name": "s4",
          "type": "FrozenArtifact"
        },
        {
          "name": "dependency_inventory",
          "type": "tuple[DependencyInventoryEntry, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "AnchoredBlob",
      "fields": [
        {
          "name": "repository_path",
          "type": "str"
        },
        {
          "name": "blob_id",
          "type": "str"
        },
        {
          "name": "sha256",
          "type": "str"
        },
        {
          "name": "octets",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "S7AnchorCreateResult",
      "fields": [
        {
          "name": "commit_sha",
          "type": "str"
        },
        {
          "name": "tree_sha",
          "type": "str"
        },
        {
          "name": "parent_commit_sha",
          "type": "str"
        },
        {
          "name": "anchored",
          "type": "tuple[AnchoredBlob, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "S7VerificationResult",
      "fields": [
        {
          "name": "passed",
          "type": "bool"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        },
        {
          "name": "anchored_digests",
          "type": "tuple[tuple[str, str], ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "VerifiedRepositoryContext",
      "fields": [
        {
          "name": "canonical_root",
          "type": "Path"
        },
        {
          "name": "git_dir",
          "type": "Path"
        },
        {
          "name": "evaluation_commit",
          "type": "str"
        },
        {
          "name": "base_controller_commit",
          "type": "str"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "root_device",
          "type": "int"
        },
        {
          "name": "root_inode",
          "type": "int"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "AnchoredS1Handle",
      "fields": [
        {
          "name": "s7_commit_sha",
          "type": "str"
        },
        {
          "name": "s1_repository_path",
          "type": "str"
        },
        {
          "name": "s1_blob_id",
          "type": "str"
        },
        {
          "name": "frozen_s1",
          "type": "FrozenArtifact"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "repository_context_token",
          "type": "str"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "N4ABoundaryPrimitive",
      "fields": [
        {
          "name": "format",
          "type": "Literal['N4A_BOUNDARY_PRIMITIVE_V1']"
        },
        {
          "name": "renderer_input_sha256",
          "type": "str"
        },
        {
          "name": "renderer_input_octets",
          "type": "int"
        },
        {
          "name": "signer_entitlements_sha256",
          "type": "str"
        },
        {
          "name": "signer_entitlements_octets",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "VerifierOwnedSealedDestination",
      "fields": [
        {
          "name": "scratch_root",
          "type": "Path"
        },
        {
          "name": "application_path",
          "type": "Path"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "repository_context_token",
          "type": "str"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "VerifierOwnedSigningIdentity",
      "fields": [
        {
          "name": "value",
          "type": "str"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "repository_context_token",
          "type": "str"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "N4ASealCapability",
      "fields": [
        {
          "name": "_generation_identity",
          "type": "str"
        },
        {
          "name": "_repository_context_token",
          "type": "str"
        },
        {
          "name": "_lifecycle_token",
          "type": "str"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "N4ATransientApplication",
      "fields": [
        {
          "name": "_generation_identity",
          "type": "str"
        },
        {
          "name": "_subject_path",
          "type": "Path"
        },
        {
          "name": "_repository_context_token",
          "type": "str"
        },
        {
          "name": "_lifecycle_token",
          "type": "str"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "VerifierOwnedBuildContext",
      "fields": [
        {
          "name": "repository_context",
          "type": "VerifiedRepositoryContext"
        },
        {
          "name": "sealed_destination",
          "type": "VerifierOwnedSealedDestination"
        },
        {
          "name": "signing_identity",
          "type": "VerifierOwnedSigningIdentity"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "_registration_token",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "N4AProductionResult",
      "fields": [
        {
          "name": "primitive",
          "type": "N4ABoundaryPrimitive"
        },
        {
          "name": "seal_capability",
          "type": "N4ASealCapability"
        },
        {
          "name": "transient_application",
          "type": "N4ATransientApplication"
        },
        {
          "name": "renderer_output_s2",
          "type": "FrozenArtifact"
        },
        {
          "name": "n4b_handoff",
          "type": "N4ASealHandoff"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "CodeDirectoryIdentity",
      "fields": [
        {
          "name": "sha256",
          "type": "str"
        },
        {
          "name": "code_limit",
          "type": "int"
        },
        {
          "name": "page_size",
          "type": "int"
        },
        {
          "name": "code_slot_sha256",
          "type": "tuple[str, ...]"
        },
        {
          "name": "special_slot_sha256",
          "type": "tuple[tuple[int, str | None], ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "SignedImageProjection",
      "fields": [
        {
          "name": "executable_code_region_bytes",
          "type": "bytes"
        },
        {
          "name": "info_plist_bytes",
          "type": "bytes"
        },
        {
          "name": "code_resources_bytes",
          "type": "bytes"
        },
        {
          "name": "superblob_index_bytes",
          "type": "bytes"
        },
        {
          "name": "code_directory_bytes",
          "type": "bytes"
        },
        {
          "name": "entitlements_blob_bytes",
          "type": "bytes"
        },
        {
          "name": "der_entitlements_blob_bytes",
          "type": "bytes"
        },
        {
          "name": "requirements_blob_sha256",
          "type": "str"
        },
        {
          "name": "cms_signature_blob_sha256",
          "type": "str"
        },
        {
          "name": "special_slot_state",
          "type": "tuple[tuple[int, bytes], ...]"
        },
        {
          "name": "signing_time_stable_code_directory_identity",
          "type": "CodeDirectoryIdentity"
        },
        {
          "name": "canonical_identity_json_bytes",
          "type": "bytes"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "VerifiedSignedImageProjectionSource",
      "fields": [
        {
          "name": "source_application",
          "type": "N4ATransientApplication"
        },
        {
          "name": "generation_identity",
          "type": "str"
        },
        {
          "name": "repository_context",
          "type": "VerifiedRepositoryContext"
        },
        {
          "name": "executable_code_region_bytes",
          "type": "bytes"
        },
        {
          "name": "info_plist_bytes",
          "type": "bytes"
        },
        {
          "name": "code_resources_bytes",
          "type": "bytes"
        },
        {
          "name": "superblob_index_bytes",
          "type": "bytes"
        },
        {
          "name": "code_directory_bytes",
          "type": "bytes"
        },
        {
          "name": "entitlements_blob_bytes",
          "type": "bytes"
        },
        {
          "name": "der_entitlements_blob_bytes",
          "type": "bytes"
        },
        {
          "name": "requirements_blob_sha256",
          "type": "str"
        },
        {
          "name": "cms_signature_blob_sha256",
          "type": "str"
        },
        {
          "name": "special_slot_state",
          "type": "tuple[tuple[int, bytes], ...]"
        },
        {
          "name": "code_directory_identity",
          "type": "CodeDirectoryIdentity"
        },
        {
          "name": "_capture_registration",
          "type": "object"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "N4ASealHandoff",
      "fields": [
        {
          "name": "measured_primitive",
          "type": "N4ABoundaryPrimitive"
        },
        {
          "name": "capability",
          "type": "N4ASealCapability"
        },
        {
          "name": "projection",
          "type": "SignedImageProjection"
        },
        {
          "name": "source_application",
          "type": "N4ATransientApplication"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "SealResult",
      "fields": [
        {
          "name": "commit_sha",
          "type": "str"
        },
        {
          "name": "tree_sha",
          "type": "str"
        },
        {
          "name": "parent_s7_commit_sha",
          "type": "str"
        },
        {
          "name": "projection_members",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "identity_json_sha256",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ParsedEntitlementPolicy",
      "fields": [
        {
          "name": "app_sandbox",
          "type": "bool"
        },
        {
          "name": "read_only_paths",
          "type": "tuple[str, ...]"
        },
        {
          "name": "read_write_paths",
          "type": "tuple[str, ...]"
        },
        {
          "name": "keys",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "S8Capture",
      "fields": [
        {
          "name": "exact_bytes",
          "type": "bytes"
        },
        {
          "name": "sha256",
          "type": "str"
        },
        {
          "name": "parsed_policy",
          "type": "ParsedEntitlementPolicy"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "DomainEvaluation",
      "fields": [
        {
          "name": "passed",
          "type": "bool"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "Tier1RowDefinition",
      "fields": [
        {
          "name": "row_id",
          "type": "int"
        },
        {
          "name": "kind",
          "type": "Tier1RowKind"
        },
        {
          "name": "predicate_ids",
          "type": "tuple[str, ...]"
        },
        {
          "name": "evaluator_id",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "Tier1RowResult",
      "fields": [
        {
          "name": "row_id",
          "type": "int"
        },
        {
          "name": "kind",
          "type": "Tier1RowKind"
        },
        {
          "name": "predicate_ids",
          "type": "tuple[str, ...]"
        },
        {
          "name": "passed",
          "type": "bool"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "Tier1GateResult",
      "fields": [
        {
          "name": "phase",
          "type": "Tier1Phase"
        },
        {
          "name": "passed",
          "type": "bool"
        },
        {
          "name": "rows",
          "type": "tuple[Tier1RowResult, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "Tier1EvaluationInputs",
      "fields": [
        {
          "name": "authority",
          "type": "DomainEvaluation"
        },
        {
          "name": "snapshots",
          "type": "DomainEvaluation"
        },
        {
          "name": "anchor",
          "type": "DomainEvaluation"
        },
        {
          "name": "boundary",
          "type": "DomainEvaluation"
        },
        {
          "name": "seal",
          "type": "DomainEvaluation"
        },
        {
          "name": "s8_policy",
          "type": "DomainEvaluation"
        },
        {
          "name": "references",
          "type": "tuple[ReferenceResolution, ...]"
        },
        {
          "name": "retention",
          "type": "tuple[RetentionEvaluation, ...]"
        },
        {
          "name": "reproducibility",
          "type": "DomainEvaluation"
        },
        {
          "name": "envelope",
          "type": "DomainEvaluation"
        },
        {
          "name": "dependency_provenance",
          "type": "DomainEvaluation"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "RetainedEventEvidence",
      "fields": [
        {
          "name": "s9_commit_sha",
          "type": "str"
        },
        {
          "name": "parent_s7_commit_sha",
          "type": "str"
        },
        {
          "name": "s13_commit_sha",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "RetainedRow21Inputs",
      "fields": [
        {
          "name": "b_commit_sha",
          "type": "str"
        },
        {
          "name": "s13_commit_sha",
          "type": "str"
        },
        {
          "name": "parent_s7_commit_sha",
          "type": "str"
        },
        {
          "name": "s8_path",
          "type": "str"
        },
        {
          "name": "s11_result_path",
          "type": "str"
        },
        {
          "name": "s1_path",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "S11Inputs",
      "fields": [
        {
          "name": "predicate_results",
          "type": "tuple[tuple[str, bool], ...]"
        },
        {
          "name": "anchored_digests",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "policy_closure_result",
          "type": "bool"
        },
        {
          "name": "decision_record_id",
          "type": "str"
        },
        {
          "name": "authority_record_sha256",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ReproducibilityInputs",
      "fields": [
        {
          "name": "exact_s1",
          "type": "FrozenArtifact"
        },
        {
          "name": "exact_s2",
          "type": "FrozenArtifact"
        },
        {
          "name": "effective_field_mutation",
          "type": "tuple[str, str]"
        },
        {
          "name": "noneffective_field_mutation",
          "type": "tuple[str, str]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ResultArtifacts",
      "fields": [
        {
          "name": "s11_bytes",
          "type": "bytes"
        },
        {
          "name": "s12_bytes",
          "type": "bytes"
        },
        {
          "name": "s10_bytes",
          "type": "bytes"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "PackageResult",
      "fields": [
        {
          "name": "s13_commit_sha",
          "type": "str"
        },
        {
          "name": "parent_s9_commit_sha",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_orchestrator",
      "name": "EvidenceDagOrchestrator",
      "fields": [
        {
          "name": "repository_context",
          "type": "VerifiedRepositoryContext"
        },
        {
          "name": "anchor",
          "type": "S7AnchorCreateResult"
        },
        {
          "name": "anchored_s1",
          "type": "AnchoredS1Handle"
        },
        {
          "name": "snapshots",
          "type": "FrozenSnapshotSet"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "P2InvalidCase",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "authority",
          "type": "AuthorityTuple"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "StableCensusObservation",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "subaction_id",
          "type": "str"
        },
        {
          "name": "trace",
          "type": "tuple[str, ...]"
        },
        {
          "name": "success",
          "type": "bool"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        },
        {
          "name": "governing_call_count",
          "type": "int"
        },
        {
          "name": "mutation_observed",
          "type": "bool"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "NormativeAdversarialRow",
      "fields": [
        {
          "name": "row_id",
          "type": "str"
        },
        {
          "name": "domain",
          "type": "str"
        },
        {
          "name": "case_text",
          "type": "str"
        },
        {
          "name": "required_outcome",
          "type": "str"
        },
        {
          "name": "domain_sha256",
          "type": "str"
        },
        {
          "name": "case_sha256",
          "type": "str"
        },
        {
          "name": "outcome_sha256",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "AdversarialExecutionRequest",
      "fields": [
        {
          "name": "row_id",
          "type": "str"
        },
        {
          "name": "action_kind",
          "type": "AdversarialActionKind"
        },
        {
          "name": "action_args",
          "type": "tuple[FixtureMutationOp, ...]"
        },
        {
          "name": "governing_callable_id",
          "type": "str"
        },
        {
          "name": "probe_id",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "AdversarialExecutionObservation",
      "fields": [
        {
          "name": "row_id",
          "type": "str"
        },
        {
          "name": "governing_callable_id",
          "type": "str"
        },
        {
          "name": "probe_id",
          "type": "str"
        },
        {
          "name": "production_call_count",
          "type": "int"
        },
        {
          "name": "process_leaf_count",
          "type": "int"
        },
        {
          "name": "mutation_observed",
          "type": "bool"
        },
        {
          "name": "post_mutation_invariant_passed",
          "type": "bool"
        },
        {
          "name": "observed_kind",
          "type": "AdversarialObservedKind"
        },
        {
          "name": "observed_failure_code",
          "type": "EvidenceFailureCode | None"
        },
        {
          "name": "observed_detail",
          "type": "str | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "ExpectedParameter",
      "fields": [
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "annotation",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "ExpectedInterface",
      "fields": [
        {
          "name": "module",
          "type": "str"
        },
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "parameters",
          "type": "tuple[ExpectedParameter, ...]"
        },
        {
          "name": "return_annotation",
          "type": "str"
        },
        {
          "name": "governed_error_type",
          "type": "str"
        },
        {
          "name": "visibility",
          "type": "Literal['PUBLIC','PRIVATE_SECURITY','TEST_SUPPORT']"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "ExpectedEnum",
      "fields": [
        {
          "name": "module",
          "type": "str"
        },
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "values",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "ExpectedDataclass",
      "fields": [
        {
          "name": "module",
          "type": "str"
        },
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "fields",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "frozen",
          "type": "bool"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ShellAssignment",
      "fields": [
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "raw_value",
          "type": "str"
        },
        {
          "name": "source_variables",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ShellArgvToken",
      "fields": [
        {
          "name": "raw",
          "type": "str"
        },
        {
          "name": "normalized",
          "type": "str"
        },
        {
          "name": "source_variables",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ShellCommand",
      "fields": [
        {
          "name": "line_no",
          "type": "int"
        },
        {
          "name": "argv_tokens",
          "type": "tuple[ShellArgvToken, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ShellSink",
      "fields": [
        {
          "name": "kind",
          "type": "ShellSinkKind"
        },
        {
          "name": "command_index",
          "type": "int"
        },
        {
          "name": "argv_index",
          "type": "int"
        },
        {
          "name": "source_variables",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ShellContract",
      "fields": [
        {
          "name": "required_nonempty_variables",
          "type": "tuple[str, ...]"
        },
        {
          "name": "assignments",
          "type": "tuple[ShellAssignment, ...]"
        },
        {
          "name": "assignment_edges",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "commands",
          "type": "tuple[ShellCommand, ...]"
        },
        {
          "name": "sinks",
          "type": "tuple[ShellSink, ...]"
        },
        {
          "name": "referenced_variables",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "EvidenceReference",
      "fields": [
        {
          "name": "reference_class",
          "type": "ReferenceClass"
        },
        {
          "name": "repository_path",
          "type": "str | None"
        },
        {
          "name": "object_id",
          "type": "str | None"
        },
        {
          "name": "expected_sha256",
          "type": "str | None"
        },
        {
          "name": "authority_ref",
          "type": "str | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ReferenceResolutionContext",
      "fields": [
        {
          "name": "s7_commit_sha",
          "type": "str"
        },
        {
          "name": "s13_commit_sha",
          "type": "str"
        },
        {
          "name": "base_controller_commit",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "ReferenceResolution",
      "fields": [
        {
          "name": "passed",
          "type": "bool"
        },
        {
          "name": "resolved_arm",
          "type": "Literal['a','b','c','d'] | None"
        },
        {
          "name": "resolved_object_id",
          "type": "str | None"
        },
        {
          "name": "resolved_sha256",
          "type": "str | None"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "RecordedEvidenceValue",
      "fields": [
        {
          "name": "artifact_role",
          "type": "Literal['S8','S9','S11','S12','S10']"
        },
        {
          "name": "key",
          "type": "str"
        },
        {
          "name": "value_kind",
          "type": "ReferenceValueKind"
        },
        {
          "name": "value",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "RetentionContext",
      "fields": [
        {
          "name": "s7_commit_sha",
          "type": "str"
        },
        {
          "name": "s9_commit_sha",
          "type": "str"
        },
        {
          "name": "s13_commit_sha",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "RetentionAssignment",
      "fields": [
        {
          "name": "value",
          "type": "RecordedEvidenceValue"
        },
        {
          "name": "mode",
          "type": "RetentionMode"
        }
      ],
      "frozen": true
    },
    {
      "module": "macos_stage_b_evidence_constants",
      "name": "RetentionEvaluation",
      "fields": [
        {
          "name": "passed",
          "type": "bool"
        },
        {
          "name": "mode",
          "type": "RetentionMode | None"
        },
        {
          "name": "resolution_kind",
          "type": "Literal['RETAINED_OBJECT','RETAINED_MEASUREMENT_RECORD'] | None"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "SyntheticSignedImage",
      "fields": [
        {
          "name": "executable_region",
          "type": "bytes"
        },
        {
          "name": "info_plist",
          "type": "bytes"
        },
        {
          "name": "code_resources",
          "type": "bytes"
        },
        {
          "name": "codedirectory",
          "type": "bytes"
        },
        {
          "name": "entitlements_blob",
          "type": "bytes"
        },
        {
          "name": "der_entitlements_blob",
          "type": "bytes"
        },
        {
          "name": "requirements_blob",
          "type": "bytes"
        },
        {
          "name": "cms_blob",
          "type": "bytes"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "CommandExerciseResult",
      "fields": [
        {
          "name": "accepted",
          "type": "bool"
        },
        {
          "name": "dependency_edges",
          "type": "tuple[bytes, ...]"
        },
        {
          "name": "failure_code",
          "type": "EvidenceFailureCode | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "SyntheticEntry",
      "fields": [
        {
          "name": "kind",
          "type": "EntryKind"
        },
        {
          "name": "data",
          "type": "bytes | None"
        },
        {
          "name": "raw_link_target",
          "type": "bytes | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "SyntheticCensusFS",
      "fields": [
        {
          "name": "start",
          "type": "PurePath"
        },
        {
          "name": "entries",
          "type": "dict[PurePath, SyntheticEntry]"
        },
        {
          "name": "expansion_count",
          "type": "int"
        },
        {
          "name": "read_counts",
          "type": "dict[PurePath, int]"
        },
        {
          "name": "host_limit",
          "type": "int | None"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ProbeEvent",
      "fields": [
        {
          "name": "kind",
          "type": "ProbeEventKind"
        },
        {
          "name": "subject",
          "type": "str"
        },
        {
          "name": "ordinal",
          "type": "int"
        },
        {
          "name": "detail",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "CensusCaseFixture",
      "fields": [
        {
          "name": "base_root",
          "type": "PurePath"
        },
        {
          "name": "venv_root",
          "type": "PurePath"
        },
        {
          "name": "fs",
          "type": "SyntheticCensusFS"
        },
        {
          "name": "trace",
          "type": "list[ProbeEvent]"
        },
        {
          "name": "mutation_state",
          "type": "tuple[tuple[str, str], ...]"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "TmpGitRepo",
      "fields": [
        {
          "name": "root",
          "type": "Path"
        },
        {
          "name": "env",
          "type": "dict[str, str]"
        },
        {
          "name": "head_commit",
          "type": "str"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "MutableNativeSource",
      "fields": [
        {
          "name": "reads",
          "type": "tuple[bytes, ...]"
        },
        {
          "name": "read_count",
          "type": "int"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "SnapshotFixture",
      "fields": [
        {
          "name": "verifier_inputs",
          "type": "VerifierSnapshotInputs"
        },
        {
          "name": "producer_inputs",
          "type": "ProducerSnapshotInputs"
        },
        {
          "name": "mutable_native_source",
          "type": "MutableNativeSource"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "RetentionFixture",
      "fields": [
        {
          "name": "context",
          "type": "RetentionContext"
        },
        {
          "name": "mode_a_value",
          "type": "RecordedEvidenceValue"
        },
        {
          "name": "requirements_mode_b_value",
          "type": "RecordedEvidenceValue"
        },
        {
          "name": "cms_mode_b_value",
          "type": "RecordedEvidenceValue"
        },
        {
          "name": "foreign_digest_value",
          "type": "RecordedEvidenceValue"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ResultBuilder",
      "fields": [
        {
          "name": "s11_inputs",
          "type": "S11Inputs"
        },
        {
          "name": "reproducibility_inputs",
          "type": "ReproducibilityInputs"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "RetainedRow21Fixture",
      "fields": [
        {
          "name": "inputs",
          "type": "RetainedRow21Inputs"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "HelperContract",
      "fields": [
        {
          "name": "owner",
          "type": "str"
        },
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "signature",
          "type": "str"
        },
        {
          "name": "semantics",
          "type": "str"
        },
        {
          "name": "governed_error_type",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "PlanContractFixture",
      "fields": [
        {
          "name": "enums",
          "type": "tuple[ExpectedEnum, ...]"
        },
        {
          "name": "dataclasses",
          "type": "tuple[ExpectedDataclass, ...]"
        },
        {
          "name": "interfaces",
          "type": "tuple[ExpectedInterface, ...]"
        },
        {
          "name": "helpers",
          "type": "tuple[HelperContract, ...]"
        },
        {
          "name": "expected_node_ids",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "OpaqueHandleForgeryCase",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "handle_kind",
          "type": "str"
        },
        {
          "name": "mutation_kind",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "StructuralCommandCase",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "command_value",
          "type": "int"
        },
        {
          "name": "variant",
          "type": "Literal['VALID','UNDERSIZED','FORMULA_OR_TRAILING','NONZERO_RESERVED_OR_PADDING']"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "Header64Case",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "fixture_id",
          "type": "str"
        },
        {
          "name": "expected_success",
          "type": "bool"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "FatStructureCase",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "fixture_id",
          "type": "str"
        },
        {
          "name": "expected_success",
          "type": "bool"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "AdversarialFixture",
      "fields": [
        {
          "name": "row_id",
          "type": "str"
        },
        {
          "name": "fixture_builder_id",
          "type": "str"
        },
        {
          "name": "fixture_state",
          "type": "bytes"
        },
        {
          "name": "resource_tokens",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "ObservationProbeHandle",
      "fields": [
        {
          "name": "probe_id",
          "type": "str"
        },
        {
          "name": "events",
          "type": "list[ProbeEvent]"
        }
      ],
      "frozen": false
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "StableCensusConstructionSpec",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "fixture_builder_id",
          "type": "str"
        },
        {
          "name": "subaction_ids",
          "type": "tuple[str, ...]"
        },
        {
          "name": "governing_callable_id",
          "type": "str"
        },
        {
          "name": "probe_observer_id",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "StableCensusSubcaseExpectation",
      "fields": [
        {
          "name": "subaction_id",
          "type": "str"
        },
        {
          "name": "expected_trace",
          "type": "tuple[str, ...]"
        },
        {
          "name": "expected_success",
          "type": "bool"
        },
        {
          "name": "expected_failure_code",
          "type": "EvidenceFailureCode | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "StableCensusExpectation",
      "fields": [
        {
          "name": "case_id",
          "type": "str"
        },
        {
          "name": "subcases",
          "type": "tuple[StableCensusSubcaseExpectation, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "OracleInspectionRequest",
      "fields": [
        {
          "name": "domain",
          "type": "OracleInspectionDomain"
        },
        {
          "name": "surface_id",
          "type": "str"
        },
        {
          "name": "production_paths",
          "type": "tuple[str, ...]"
        },
        {
          "name": "mechanism",
          "type": "OracleInspectionMechanism"
        },
        {
          "name": "forbidden_form",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "OracleInspectionExpectation",
      "fields": [
        {
          "name": "surface_id",
          "type": "str"
        },
        {
          "name": "expected",
          "type": "OracleExpectedResult"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "OracleInspectionObservation",
      "fields": [
        {
          "name": "surface_id",
          "type": "str"
        },
        {
          "name": "mechanism",
          "type": "OracleInspectionMechanism"
        },
        {
          "name": "matches",
          "type": "tuple[str, ...]"
        },
        {
          "name": "reachable_symbols",
          "type": "tuple[str, ...]"
        },
        {
          "name": "import_resolution",
          "type": "tuple[str, ...]"
        },
        {
          "name": "import_succeeded",
          "type": "bool | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "PostMutationInvariant",
      "fields": [
        {
          "name": "observer_id",
          "type": "str"
        },
        {
          "name": "expected_state_sha256",
          "type": "str"
        },
        {
          "name": "required_targets",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "AdversarialConstructionSpec",
      "fields": [
        {
          "name": "row_id",
          "type": "str"
        },
        {
          "name": "normative_row_sha256",
          "type": "str"
        },
        {
          "name": "domain",
          "type": "str"
        },
        {
          "name": "builder_id",
          "type": "str"
        },
        {
          "name": "action_kind",
          "type": "AdversarialActionKind"
        },
        {
          "name": "action_args",
          "type": "tuple[FixtureMutationOp, ...]"
        },
        {
          "name": "governing_callable_id",
          "type": "str"
        },
        {
          "name": "probe_id",
          "type": "str"
        },
        {
          "name": "post_mutation_invariant",
          "type": "PostMutationInvariant"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "AdversarialExpectation",
      "fields": [
        {
          "name": "row_id",
          "type": "str"
        },
        {
          "name": "expected_kind",
          "type": "AdversarialObservedKind"
        },
        {
          "name": "expected_failure_code",
          "type": "EvidenceFailureCode | None"
        },
        {
          "name": "expected_detail",
          "type": "str | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "ExpectedProtocolMethod",
      "fields": [
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "parameters",
          "type": "tuple[ExpectedParameter, ...]"
        },
        {
          "name": "return_annotation",
          "type": "str"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "ExpectedProtocol",
      "fields": [
        {
          "name": "module",
          "type": "str"
        },
        {
          "name": "name",
          "type": "str"
        },
        {
          "name": "classification",
          "type": "Literal['PROTOCOL']"
        },
        {
          "name": "methods",
          "type": "tuple[ExpectedProtocolMethod, ...]"
        },
        {
          "name": "visibility",
          "type": "Literal['PUBLIC','PRIVATE_SECURITY','TEST_SUPPORT']"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ShellCommandFamilyRule",
      "fields": [
        {
          "name": "family",
          "type": "ShellCommandFamily"
        },
        {
          "name": "executables",
          "type": "tuple[str, ...]"
        },
        {
          "name": "context",
          "type": "str"
        },
        {
          "name": "argv_shape",
          "type": "tuple[str, ...]"
        },
        {
          "name": "allowed_options",
          "type": "tuple[str, ...]"
        },
        {
          "name": "source_positions",
          "type": "tuple[tuple[int, str], ...]"
        },
        {
          "name": "sink_positions",
          "type": "tuple[tuple[int, ShellSinkKind], ...]"
        },
        {
          "name": "aliases_may_feed_sinks",
          "type": "bool"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "EffectPolicy",
      "fields": [
        {
          "name": "schema",
          "type": "Literal['G0_REV18_V7_EFFECT_POLICY_V1']"
        },
        {
          "name": "production_roots",
          "type": "tuple[str, ...]"
        },
        {
          "name": "safe_import_prefixes",
          "type": "tuple[str, ...]"
        },
        {
          "name": "forbidden_network_prefixes",
          "type": "tuple[str, ...]"
        },
        {
          "name": "process_effect_rules",
          "type": "tuple[str, ...]"
        },
        {
          "name": "traversal_effect_rules",
          "type": "tuple[str, ...]"
        },
        {
          "name": "os_harmless_call_allowlist",
          "type": "tuple[str, ...]"
        },
        {
          "name": "asyncio_harmless_call_allowlist",
          "type": "tuple[str, ...]"
        },
        {
          "name": "path_harmless_call_allowlist",
          "type": "tuple[str, ...]"
        },
        {
          "name": "path_constructor_policy",
          "type": "Literal['CONSTRUCTION_ONLY_NO_EFFECT']"
        },
        {
          "name": "path_binding_resolution_policy",
          "type": "str"
        },
        {
          "name": "path_unlisted_callable_policy",
          "type": "Literal['EFFECT_UNKNOWN_FAIL_CLOSED']"
        },
        {
          "name": "multiprocessing_policy",
          "type": "Literal['FAIL_CLOSED_IMPORT_OR_CALL']"
        },
        {
          "name": "allowed_process_leaves",
          "type": "tuple[str, ...]"
        },
        {
          "name": "allowed_traversal_leaf",
          "type": "str"
        },
        {
          "name": "local_module_call_resolution_policy",
          "type": "str"
        },
        {
          "name": "unresolved_dynamic_local_edge_policy",
          "type": "Literal['FAIL_CLOSED']"
        },
        {
          "name": "unknown_external_import_policy",
          "type": "Literal['FAIL_CLOSED']"
        },
        {
          "name": "security_relevant_unlisted_call_policy",
          "type": "Literal['EFFECT_UNKNOWN_FAIL_CLOSED']"
        },
        {
          "name": "shell_true_policy",
          "type": "Literal['FAIL_CLOSED']"
        },
        {
          "name": "network_allowlist",
          "type": "tuple[str, ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "EffectScanFinding",
      "fields": [
        {
          "name": "kind",
          "type": "EffectKind"
        },
        {
          "name": "module",
          "type": "str"
        },
        {
          "name": "function",
          "type": "str"
        },
        {
          "name": "symbol",
          "type": "str"
        },
        {
          "name": "line",
          "type": "int"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "EffectScanResult",
      "fields": [
        {
          "name": "findings",
          "type": "tuple[EffectScanFinding, ...]"
        },
        {
          "name": "resolved_local_edges",
          "type": "tuple[tuple[str, str], ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "CommandLedgerEvent",
      "fields": [
        {
          "name": "schema",
          "type": "Literal['gate0-rev18-controlled-run-ledger.v3']"
        },
        {
          "name": "event_sequence",
          "type": "int"
        },
        {
          "name": "command_sequence",
          "type": "int"
        },
        {
          "name": "marker",
          "type": "LedgerEventMarker"
        },
        {
          "name": "argv",
          "type": "tuple[str, ...]"
        },
        {
          "name": "cwd",
          "type": "str"
        },
        {
          "name": "environment",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "control_inputs",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "task_step_id",
          "type": "str"
        },
        {
          "name": "stdin_mode",
          "type": "StdinMode"
        },
        {
          "name": "stdin_octets",
          "type": "int"
        },
        {
          "name": "stdin_sha256",
          "type": "str | None"
        },
        {
          "name": "exit_status",
          "type": "int | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "PytestRecorderSnapshot",
      "fields": [
        {
          "name": "schema",
          "type": "Literal['gate0-rev18-pytest-recorder.v4']"
        },
        {
          "name": "pre_deselection_node_ids",
          "type": "tuple[str, ...]"
        },
        {
          "name": "deselected_node_ids",
          "type": "tuple[str, ...]"
        },
        {
          "name": "executed_node_ids",
          "type": "tuple[str, ...]"
        },
        {
          "name": "collection_errors",
          "type": "tuple[tuple[str, str, str], ...]"
        },
        {
          "name": "outcomes",
          "type": "tuple[tuple[str, HistoricalOutcome], ...]"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "FixtureMutationOp",
      "fields": [
        {
          "name": "opcode",
          "type": "FixtureMutationOpcode"
        },
        {
          "name": "target",
          "type": "str"
        },
        {
          "name": "value",
          "type": "str"
        },
        {
          "name": "aux",
          "type": "str | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "AllowedControlledCommand",
      "fields": [
        {
          "name": "task_step_id",
          "type": "str"
        },
        {
          "name": "argv",
          "type": "tuple[str, ...]"
        },
        {
          "name": "cwd_policy",
          "type": "Literal['EXACT_REPOSITORY_ROOT']"
        },
        {
          "name": "selected_environment_policy",
          "type": "str"
        },
        {
          "name": "required_control_keys",
          "type": "tuple[str, ...]"
        },
        {
          "name": "stdin_mode",
          "type": "StdinMode"
        },
        {
          "name": "stdin_block_id",
          "type": "str | None"
        },
        {
          "name": "expected_stdin_octets",
          "type": "int"
        },
        {
          "name": "expected_stdin_sha256",
          "type": "str | None"
        }
      ],
      "frozen": true
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "SyntheticForbiddenSourceForm",
      "fields": [
        {
          "name": "source_form_id",
          "type": "str"
        },
        {
          "name": "artifact_kind",
          "type": "SyntheticSourceArtifactKind"
        },
        {
          "name": "target_path_or_module",
          "type": "str"
        },
        {
          "name": "utf8_text",
          "type": "str"
        },
        {
          "name": "template_parameters",
          "type": "tuple[tuple[str, str], ...]"
        },
        {
          "name": "required_property",
          "type": "str"
        },
        {
          "name": "observer_id",
          "type": "str"
        },
        {
          "name": "canonical_observation",
          "type": "str"
        }
      ],
      "frozen": true
    }
  ],
  "callables": [
    {
      "module": "macos_stage_b_evidence_runtime",
      "name": "canonicalize_path_v1",
      "parameters": [
        {
          "name": "path",
          "annotation": "PurePath"
        },
        {
          "name": "fs",
          "annotation": "CensusFS"
        }
      ],
      "return_annotation": "CanonicalizationResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_runtime",
      "name": "capture_stable_census",
      "parameters": [
        {
          "name": "base_root",
          "annotation": "PurePath"
        },
        {
          "name": "venv_root",
          "annotation": "PurePath"
        },
        {
          "name": "fs",
          "annotation": "CensusFS"
        }
      ],
      "return_annotation": "StableCensusResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_runtime",
      "name": "serialize_native_manifest",
      "parameters": [
        {
          "name": "result",
          "annotation": "StableCensusResult"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_runtime",
      "name": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
      "parameters": [
        {
          "name": "data",
          "annotation": "bytes"
        }
      ],
      "return_annotation": "NativeCandidateClassification",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_macho",
      "name": "MACHO_NATIVE_CONTAINER_PARSE_V1",
      "parameters": [
        {
          "name": "data",
          "annotation": "bytes"
        }
      ],
      "return_annotation": "ParsedMachO",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "read_blob_at",
      "parameters": [
        {
          "name": "commit_sha",
          "annotation": "str"
        },
        {
          "name": "repository_path",
          "annotation": "str"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "blob_id_at",
      "parameters": [
        {
          "name": "commit_sha",
          "annotation": "str"
        },
        {
          "name": "repository_path",
          "annotation": "str"
        }
      ],
      "return_annotation": "str",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "object_type",
      "parameters": [
        {
          "name": "object_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "Literal['commit','tree','blob']",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "commit_parent",
      "parameters": [
        {
          "name": "commit_sha",
          "annotation": "str"
        }
      ],
      "return_annotation": "str",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "commit_tree",
      "parameters": [
        {
          "name": "commit_sha",
          "annotation": "str"
        }
      ],
      "return_annotation": "str",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "strict_ancestor",
      "parameters": [
        {
          "name": "ancestor_commit",
          "annotation": "str"
        },
        {
          "name": "descendant_commit",
          "annotation": "str"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "reachable_committed_generation_identities",
      "parameters": [
        {
          "name": "evaluation_commit",
          "annotation": "str"
        }
      ],
      "return_annotation": "tuple[str, ...]",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "additive_mdrt_paths",
      "parameters": [
        {
          "name": "base_commit",
          "annotation": "str"
        },
        {
          "name": "head_commit",
          "annotation": "str"
        }
      ],
      "return_annotation": "tuple[str, ...]",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "verify_repository_context",
      "parameters": [
        {
          "name": "authority",
          "annotation": "AuthorityTuple"
        },
        {
          "name": "evaluation_commit",
          "annotation": "str"
        }
      ],
      "return_annotation": "VerifiedRepositoryContext",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "_validate_verified_repository_context",
      "parameters": [
        {
          "name": "context",
          "annotation": "VerifiedRepositoryContext"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "_run_git",
      "parameters": [
        {
          "name": "argv",
          "annotation": "tuple[str, ...]"
        },
        {
          "name": "cwd",
          "annotation": "Path"
        }
      ],
      "return_annotation": "subprocess.CompletedProcess[bytes]",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_authority",
      "name": "derive_generation_identity",
      "parameters": [
        {
          "name": "authority",
          "annotation": "AuthorityTuple"
        }
      ],
      "return_annotation": "str",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_authority",
      "name": "validate_s4_a2r_m1r_echo",
      "parameters": [
        {
          "name": "s4_bytes",
          "annotation": "bytes"
        },
        {
          "name": "authority",
          "annotation": "AuthorityTuple"
        }
      ],
      "return_annotation": "DomainEvaluation",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_snapshot",
      "name": "derive_frozen_snapshots",
      "parameters": [
        {
          "name": "verifier_inputs",
          "annotation": "VerifierSnapshotInputs"
        },
        {
          "name": "producer_inputs",
          "annotation": "ProducerSnapshotInputs"
        }
      ],
      "return_annotation": "FrozenSnapshotSet",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_snapshot",
      "name": "render_s2_from_s1",
      "parameters": [
        {
          "name": "s1",
          "annotation": "FrozenArtifact"
        }
      ],
      "return_annotation": "FrozenArtifact",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_snapshot",
      "name": "_derive_dependency_inventory_from_host",
      "parameters": [
        {
          "name": "verifier_inputs",
          "annotation": "VerifierSnapshotInputs"
        }
      ],
      "return_annotation": "tuple[DependencyInventoryEntry, ...]",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_snapshot",
      "name": "_read_host_native_image",
      "parameters": [
        {
          "name": "path",
          "annotation": "Path"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_anchor",
      "name": "create_s7_anchor",
      "parameters": [
        {
          "name": "parent_commit_sha",
          "annotation": "str"
        },
        {
          "name": "artifacts",
          "annotation": "tuple[FrozenArtifact, FrozenArtifact, FrozenArtifact, FrozenArtifact]"
        }
      ],
      "return_annotation": "S7AnchorCreateResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_anchor",
      "name": "verify_s7_anchor",
      "parameters": [
        {
          "name": "anchor",
          "annotation": "S7AnchorCreateResult"
        },
        {
          "name": "artifacts",
          "annotation": "tuple[FrozenArtifact, FrozenArtifact, FrozenArtifact, FrozenArtifact]"
        }
      ],
      "return_annotation": "S7VerificationResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_anchor",
      "name": "resolve_anchored_s1",
      "parameters": [
        {
          "name": "repository_context",
          "annotation": "VerifiedRepositoryContext"
        },
        {
          "name": "anchor",
          "annotation": "S7AnchorCreateResult"
        }
      ],
      "return_annotation": "AnchoredS1Handle",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_anchor",
      "name": "_extract_registered_anchored_s1",
      "parameters": [
        {
          "name": "handle",
          "annotation": "AnchoredS1Handle"
        },
        {
          "name": "repository_context",
          "annotation": "VerifiedRepositoryContext"
        }
      ],
      "return_annotation": "FrozenArtifact",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_boundary",
      "name": "_create_verifier_owned_build_context",
      "parameters": [
        {
          "name": "repository_context",
          "annotation": "VerifiedRepositoryContext"
        },
        {
          "name": "anchor",
          "annotation": "S7AnchorCreateResult"
        }
      ],
      "return_annotation": "VerifierOwnedBuildContext",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_boundary",
      "name": "invoke_stage_b_build_app",
      "parameters": [
        {
          "name": "s2",
          "annotation": "FrozenArtifact"
        },
        {
          "name": "build_context",
          "annotation": "VerifierOwnedBuildContext"
        }
      ],
      "return_annotation": "N4ATransientApplication",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_boundary",
      "name": "measure_and_handoff_n4a",
      "parameters": [
        {
          "name": "anchored_s1",
          "annotation": "AnchoredS1Handle"
        },
        {
          "name": "anchored_s2",
          "annotation": "FrozenArtifact"
        },
        {
          "name": "build_context",
          "annotation": "VerifierOwnedBuildContext"
        }
      ],
      "return_annotation": "N4AProductionResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_boundary",
      "name": "_run_stage_b_build_process",
      "parameters": [
        {
          "name": "s2",
          "annotation": "FrozenArtifact"
        },
        {
          "name": "build_context",
          "annotation": "VerifierOwnedBuildContext"
        },
        {
          "name": "private_s2_file",
          "annotation": "Path"
        },
        {
          "name": "env",
          "annotation": "dict[str, str]"
        }
      ],
      "return_annotation": "subprocess.CompletedProcess[bytes]",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_boundary",
      "name": "_validate_registered_handle",
      "parameters": [
        {
          "name": "handle",
          "annotation": "VerifierOwnedSealedDestination | VerifierOwnedSigningIdentity | VerifierOwnedBuildContext | N4ASealCapability | N4ATransientApplication"
        },
        {
          "name": "repository_context",
          "annotation": "VerifiedRepositoryContext"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_projection",
      "name": "project_signed_image",
      "parameters": [
        {
          "name": "image",
          "annotation": "SyntheticSignedImage"
        }
      ],
      "return_annotation": "SignedImageProjection",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_seal",
      "name": "seal_n4b",
      "parameters": [
        {
          "name": "s7",
          "annotation": "S7AnchorCreateResult"
        },
        {
          "name": "capability",
          "annotation": "N4ASealCapability"
        }
      ],
      "return_annotation": "SealResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_s8",
      "name": "extract_s8_from_n4a_application",
      "parameters": [
        {
          "name": "application",
          "annotation": "N4ATransientApplication"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_s8",
      "name": "capture_and_evaluate_s8",
      "parameters": [
        {
          "name": "application",
          "annotation": "N4ATransientApplication"
        },
        {
          "name": "exact_s1",
          "annotation": "FrozenArtifact"
        },
        {
          "name": "seal",
          "annotation": "SealResult"
        }
      ],
      "return_annotation": "S8Capture",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_s8",
      "name": "_run_codesign_entitlements",
      "parameters": [
        {
          "name": "application",
          "annotation": "N4ATransientApplication"
        }
      ],
      "return_annotation": "subprocess.CompletedProcess[bytes]",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "macos_stage_b_evidence_references",
      "name": "resolve_p19_reference",
      "parameters": [
        {
          "name": "reference",
          "annotation": "EvidenceReference"
        },
        {
          "name": "context",
          "annotation": "ReferenceResolutionContext"
        }
      ],
      "return_annotation": "ReferenceResolution",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_retention",
      "name": "assign_p20_retention",
      "parameters": [
        {
          "name": "value",
          "annotation": "RecordedEvidenceValue"
        },
        {
          "name": "context",
          "annotation": "RetentionContext"
        }
      ],
      "return_annotation": "RetentionAssignment",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_retention",
      "name": "evaluate_p20_retention",
      "parameters": [
        {
          "name": "assignment",
          "annotation": "RetentionAssignment"
        },
        {
          "name": "context",
          "annotation": "RetentionContext"
        }
      ],
      "return_annotation": "RetentionEvaluation",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_results",
      "name": "serialize_s11",
      "parameters": [
        {
          "name": "inputs",
          "annotation": "S11Inputs"
        },
        {
          "name": "tier1_result",
          "annotation": "Tier1GateResult"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_results",
      "name": "build_result_artifacts",
      "parameters": [
        {
          "name": "inputs",
          "annotation": "S11Inputs"
        },
        {
          "name": "tier1_result",
          "annotation": "Tier1GateResult"
        },
        {
          "name": "reproducibility_inputs",
          "annotation": "ReproducibilityInputs"
        },
        {
          "name": "seal",
          "annotation": "SealResult"
        },
        {
          "name": "s8",
          "annotation": "S8Capture"
        }
      ],
      "return_annotation": "ResultArtifacts",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_package",
      "name": "create_s13_package",
      "parameters": [
        {
          "name": "s9_commit_sha",
          "annotation": "str"
        },
        {
          "name": "result_artifacts",
          "annotation": "ResultArtifacts"
        },
        {
          "name": "s8",
          "annotation": "S8Capture"
        }
      ],
      "return_annotation": "PackageResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_gate",
      "name": "evaluate_tier1_preentry",
      "parameters": [
        {
          "name": "inputs",
          "annotation": "Tier1EvaluationInputs"
        }
      ],
      "return_annotation": "Tier1GateResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_gate",
      "name": "evaluate_tier1_generation",
      "parameters": [
        {
          "name": "inputs",
          "annotation": "Tier1EvaluationInputs"
        },
        {
          "name": "retained",
          "annotation": "RetainedEventEvidence"
        }
      ],
      "return_annotation": "Tier1GateResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_gate",
      "name": "evaluate_tier1_later_audit",
      "parameters": [
        {
          "name": "inputs",
          "annotation": "Tier1EvaluationInputs"
        },
        {
          "name": "retained",
          "annotation": "RetainedEventEvidence"
        }
      ],
      "return_annotation": "Tier1GateResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_gate",
      "name": "evaluate_row21_retained_reverification",
      "parameters": [
        {
          "name": "retained",
          "annotation": "RetainedRow21Inputs"
        }
      ],
      "return_annotation": "Tier1RowResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_orchestrator",
      "name": "EvidenceDagOrchestrator.evaluate_generation_gate",
      "parameters": [],
      "return_annotation": "Tier1GateResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_orchestrator",
      "name": "EvidenceDagOrchestrator.serialize_s11_with",
      "parameters": [
        {
          "name": "gate",
          "annotation": "Tier1GateResult"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "macos_stage_b_evidence_orchestrator",
      "name": "EvidenceDagOrchestrator.verify_retained_package",
      "parameters": [
        {
          "name": "retained",
          "annotation": "RetainedRow21Inputs"
        }
      ],
      "return_annotation": "Tier1RowResult",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PUBLIC"
    },
    {
      "module": "scripts.stage-b-evidence-dag",
      "name": "build_parser",
      "parameters": [],
      "return_annotation": "argparse.ArgumentParser",
      "governed_error_type": "ValueError",
      "visibility": "PUBLIC"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "parse_stage_b_shell_contract",
      "parameters": [
        {
          "name": "text",
          "annotation": "str"
        }
      ],
      "return_annotation": "ShellContract",
      "governed_error_type": "ShellContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "contract_source_reaches_sink",
      "parameters": [
        {
          "name": "contract",
          "annotation": "ShellContract"
        },
        {
          "name": "source_variable",
          "annotation": "str"
        },
        {
          "name": "sink_kind",
          "annotation": "ShellSinkKind"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "load_plan_contract",
      "parameters": [
        {
          "name": "plan_path",
          "annotation": "Path"
        }
      ],
      "return_annotation": "PlanContractFixture",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "PlanContractFixture.expand_expected_new_test_node_ids",
      "parameters": [],
      "return_annotation": "tuple[str, ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "PlanContractFixture.enum_values",
      "parameters": [
        {
          "name": "name",
          "annotation": "str"
        }
      ],
      "return_annotation": "tuple[str, ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "PlanContractFixture.effect_scanner_source_contract_bytes",
      "parameters": [],
      "return_annotation": "bytes",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "TmpGitRepo.commit_file",
      "parameters": [
        {
          "name": "path",
          "annotation": "str"
        },
        {
          "name": "data",
          "annotation": "bytes"
        }
      ],
      "return_annotation": "str",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "TmpGitRepo.write_worktree",
      "parameters": [
        {
          "name": "path",
          "annotation": "str"
        },
        {
          "name": "data",
          "annotation": "bytes"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "TmpGitRepo.commit_s10_generation_ids",
      "parameters": [
        {
          "name": "generation_ids",
          "annotation": "tuple[str, ...]"
        }
      ],
      "return_annotation": "str",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "TmpGitRepo.commit_required_authority_paths",
      "parameters": [],
      "return_annotation": "str",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ResultBuilder.create_s10_before_s12",
      "parameters": [],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "execute_handle_forgery_case",
      "parameters": [
        {
          "name": "case",
          "annotation": "OpaqueHandleForgeryCase"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "build_structural_case_bytes",
      "parameters": [
        {
          "name": "case",
          "annotation": "StructuralCommandCase"
        }
      ],
      "return_annotation": "bytes",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "execute_header64_case",
      "parameters": [
        {
          "name": "case",
          "annotation": "Header64Case"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "execute_fat_structure_case",
      "parameters": [
        {
          "name": "case",
          "annotation": "FatStructureCase"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "macos_stage_b_evidence_git",
      "name": "_discover_repository_root_from_module_location",
      "parameters": [],
      "return_annotation": "Path",
      "governed_error_type": "EvidenceDagError",
      "visibility": "PRIVATE_SECURITY"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "execute_stable_census_construction",
      "parameters": [
        {
          "name": "spec",
          "annotation": "StableCensusConstructionSpec"
        }
      ],
      "return_annotation": "tuple[StableCensusObservation, ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "compare_stable_census",
      "parameters": [
        {
          "name": "observations",
          "annotation": "tuple[StableCensusObservation, ...]"
        },
        {
          "name": "expectation",
          "annotation": "StableCensusExpectation"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "inspect_oracle_request",
      "parameters": [
        {
          "name": "request",
          "annotation": "OracleInspectionRequest"
        }
      ],
      "return_annotation": "OracleInspectionObservation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "compare_oracle_observation",
      "parameters": [
        {
          "name": "observation",
          "annotation": "OracleInspectionObservation"
        },
        {
          "name": "expectation",
          "annotation": "OracleInspectionExpectation"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "construction_for",
      "parameters": [
        {
          "name": "normative_row",
          "annotation": "NormativeAdversarialRow"
        }
      ],
      "return_annotation": "AdversarialConstructionSpec",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "expectation_for",
      "parameters": [
        {
          "name": "row_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "AdversarialExpectation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "build_adversarial_fixture",
      "parameters": [
        {
          "name": "builder_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "AdversarialFixture",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "apply_adversarial_action",
      "parameters": [
        {
          "name": "action_kind",
          "annotation": "AdversarialActionKind"
        },
        {
          "name": "action_args",
          "annotation": "tuple[FixtureMutationOp, ...]"
        },
        {
          "name": "fixture",
          "annotation": "AdversarialFixture"
        }
      ],
      "return_annotation": "AdversarialFixture",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "observe_post_mutation",
      "parameters": [
        {
          "name": "fixture",
          "annotation": "AdversarialFixture"
        },
        {
          "name": "invariant",
          "annotation": "PostMutationInvariant"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "install_observation_probe",
      "parameters": [
        {
          "name": "probe_id",
          "annotation": "str"
        },
        {
          "name": "governing_callable_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "ObservationProbeHandle",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "invoke_governing_adversarial_callable",
      "parameters": [
        {
          "name": "request",
          "annotation": "AdversarialExecutionRequest"
        },
        {
          "name": "fixture",
          "annotation": "AdversarialFixture"
        },
        {
          "name": "probe",
          "annotation": "ObservationProbeHandle"
        }
      ],
      "return_annotation": "AdversarialExecutionObservation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "compare_adversarial_observation",
      "parameters": [
        {
          "name": "observation",
          "annotation": "AdversarialExecutionObservation"
        },
        {
          "name": "expectation",
          "annotation": "AdversarialExpectation"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "scan_production_effects",
      "parameters": [
        {
          "name": "policy",
          "annotation": "EffectPolicy"
        }
      ],
      "return_annotation": "EffectScanResult",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "census_construction",
      "parameters": [
        {
          "name": "case_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "StableCensusConstructionSpec",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "census_expectation",
      "parameters": [
        {
          "name": "case_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "StableCensusExpectation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "expectation_for_subaction",
      "parameters": [
        {
          "name": "expectation",
          "annotation": "StableCensusExpectation"
        },
        {
          "name": "subaction_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "StableCensusExpectation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "run_census_cheat_falsifier",
      "parameters": [
        {
          "name": "cheat",
          "annotation": "str"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "oracle_expectation_for",
      "parameters": [
        {
          "name": "surface_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "OracleInspectionExpectation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "positive_falsifier_for",
      "parameters": [
        {
          "name": "mechanism",
          "annotation": "OracleInspectionMechanism"
        }
      ],
      "return_annotation": "tuple[OracleInspectionRequest, SyntheticSourceTree]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "inspect_oracle_request_against_tree",
      "parameters": [
        {
          "name": "request",
          "annotation": "OracleInspectionRequest"
        },
        {
          "name": "tree",
          "annotation": "SyntheticSourceTree"
        }
      ],
      "return_annotation": "OracleInspectionObservation",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "observation_has_forbidden_match",
      "parameters": [
        {
          "name": "observation",
          "annotation": "OracleInspectionObservation"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
      "name": "oracle_echo_inspector_falsifier",
      "parameters": [],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "run_stage_replacement_falsifier",
      "parameters": [
        {
          "name": "stage",
          "annotation": "str"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "plan_family_rule",
      "parameters": [
        {
          "name": "family",
          "annotation": "ShellCommandFamily"
        }
      ],
      "return_annotation": "ShellCommandFamilyRule",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "derived_family_sinks",
      "parameters": [
        {
          "name": "contract",
          "annotation": "ShellContract"
        },
        {
          "name": "family",
          "annotation": "ShellCommandFamily"
        }
      ],
      "return_annotation": "tuple[tuple[int, ShellSinkKind], ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "PlanContractFixture.protocol",
      "parameters": [
        {
          "name": "name",
          "annotation": "str"
        }
      ],
      "return_annotation": "ExpectedProtocol",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "ExactOutcomeRecorder.snapshot",
      "parameters": [],
      "return_annotation": "dict[str, object]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "PlanContractFixture.unbound_fixture_references",
      "parameters": [],
      "return_annotation": "tuple[str, ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "exact_protocol_shape",
      "parameters": [
        {
          "name": "protocol_type",
          "annotation": "type"
        }
      ],
      "return_annotation": "ExpectedProtocol",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "exercise_recorder_case",
      "parameters": [
        {
          "name": "case_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "HistoricalOutcome",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "scan_synthetic_effect_source",
      "parameters": [
        {
          "name": "source",
          "annotation": "str"
        }
      ],
      "return_annotation": "EffectScanResult",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "validate_controlled_run_ledger",
      "parameters": [
        {
          "name": "events",
          "annotation": "tuple[CommandLedgerEvent, ...]"
        },
        {
          "name": "phase",
          "annotation": "str"
        },
        {
          "name": "implementation_base_sha",
          "annotation": "str"
        },
        {
          "name": "approved_plan_blob_sha",
          "annotation": "str"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "validate_changed_path_set",
      "parameters": [
        {
          "name": "changed_paths",
          "annotation": "tuple[str, ...]"
        },
        {
          "name": "phase",
          "annotation": "str"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "prohibited_generated_artifact_present",
      "parameters": [
        {
          "name": "before",
          "annotation": "tuple[str, ...]"
        },
        {
          "name": "after",
          "annotation": "tuple[str, ...]"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_fv2",
      "parameters": [
        {
          "name": "plan_path",
          "annotation": "Path"
        },
        {
          "name": "baseline_path",
          "annotation": "Path"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_fv3",
      "parameters": [
        {
          "name": "plan_path",
          "annotation": "Path"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_fv4",
      "parameters": [
        {
          "name": "plan_path",
          "annotation": "Path"
        },
        {
          "name": "ledger_path",
          "annotation": "Path"
        },
        {
          "name": "before_snapshot_path",
          "annotation": "Path"
        },
        {
          "name": "phase",
          "annotation": "str"
        },
        {
          "name": "receipt_path",
          "annotation": "Path | None"
        },
        {
          "name": "implementation_base_sha",
          "annotation": "str"
        },
        {
          "name": "approved_plan_blob_sha",
          "annotation": "str"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_fv5",
      "parameters": [
        {
          "name": "base_sha",
          "annotation": "str"
        },
        {
          "name": "phase",
          "annotation": "str"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_fv6",
      "parameters": [
        {
          "name": "repository_root",
          "annotation": "Path"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_fv8",
      "parameters": [
        {
          "name": "plan_path",
          "annotation": "Path"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "effect_policy_from_mapping",
      "parameters": [
        {
          "name": "mapping",
          "annotation": "Mapping[str, object]"
        }
      ],
      "return_annotation": "EffectPolicy",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "validate_command_event_pair",
      "parameters": [
        {
          "name": "start",
          "annotation": "CommandLedgerEvent"
        },
        {
          "name": "end",
          "annotation": "CommandLedgerEvent"
        },
        {
          "name": "allowed",
          "annotation": "AllowedControlledCommand"
        },
        {
          "name": "expected_control_inputs",
          "annotation": "tuple[tuple[str, str], ...]"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "validate_source_form_registry",
      "parameters": [
        {
          "name": "registry",
          "annotation": "tuple[SyntheticForbiddenSourceForm, ...]"
        },
        {
          "name": "used_ids",
          "annotation": "tuple[str, ...]"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "source_form_for",
      "parameters": [
        {
          "name": "source_form_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "SyntheticForbiddenSourceForm",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "used_insert_source_form_ids",
      "parameters": [
        {
          "name": "constructions",
          "annotation": "tuple[AdversarialConstructionSpec, ...]"
        }
      ],
      "return_annotation": "tuple[str, ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "observe_source_form_property",
      "parameters": [
        {
          "name": "fixture",
          "annotation": "AdversarialFixture"
        },
        {
          "name": "source_form",
          "annotation": "SyntheticForbiddenSourceForm"
        }
      ],
      "return_annotation": "bool",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "construction_for_id",
      "parameters": [
        {
          "name": "row_id",
          "annotation": "str"
        }
      ],
      "return_annotation": "AdversarialConstructionSpec",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
      "name": "insert_source_form_into_neutral_fixture",
      "parameters": [
        {
          "name": "source_form",
          "annotation": "SyntheticForbiddenSourceForm"
        }
      ],
      "return_annotation": "AdversarialFixture",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "exact_ledger_pair_for",
      "parameters": [
        {
          "name": "allowed",
          "annotation": "AllowedControlledCommand"
        },
        {
          "name": "control_inputs",
          "annotation": "tuple[tuple[str, str], ...] | None"
        }
      ],
      "return_annotation": "tuple[CommandLedgerEvent, CommandLedgerEvent]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "write_effect_policy_variant",
      "parameters": [
        {
          "name": "tmp_path",
          "annotation": "Path"
        },
        {
          "name": "contract",
          "annotation": "PlanContractFixture"
        },
        {
          "name": "mode",
          "annotation": "str"
        },
        {
          "name": "field",
          "annotation": "str"
        }
      ],
      "return_annotation": "Path",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_approved_plan_identity",
      "parameters": [
        {
          "name": "repository_root",
          "annotation": "Path"
        },
        {
          "name": "plan_path",
          "annotation": "Path"
        },
        {
          "name": "approved_plan_blob_sha",
          "annotation": "str"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_interface_manifest",
      "name": "verify_effect_scanner_source_contract",
      "parameters": [
        {
          "name": "plan_path",
          "annotation": "Path"
        },
        {
          "name": "scanner_path",
          "annotation": "Path"
        }
      ],
      "return_annotation": "None",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "exact_controlled_run_ledger_for",
      "parameters": [
        {
          "name": "contract",
          "annotation": "PlanContractFixture"
        },
        {
          "name": "phase",
          "annotation": "str"
        },
        {
          "name": "implementation_base_sha",
          "annotation": "str"
        },
        {
          "name": "approved_plan_blob_sha",
          "annotation": "str"
        }
      ],
      "return_annotation": "tuple[CommandLedgerEvent, ...]",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    },
    {
      "module": "tests.gate0.unit.evidence_dag_fixtures",
      "name": "write_scanner_contract_fixture",
      "parameters": [
        {
          "name": "tmp_path",
          "annotation": "Path"
        },
        {
          "name": "source",
          "annotation": "bytes"
        }
      ],
      "return_annotation": "Path",
      "governed_error_type": "TestContractError",
      "visibility": "TEST_SUPPORT"
    }
  ],
  "protocols": [
    {
      "module": "macos_stage_b_evidence_runtime",
      "name": "CensusFS",
      "visibility": "PUBLIC",
      "methods": [
        {
          "name": "list_entries",
          "parameters": [
            {
              "name": "directory",
              "annotation": "PurePath"
            }
          ],
          "return_annotation": "tuple[FSEntryObservation, ...]"
        },
        {
          "name": "lstat_kind",
          "parameters": [
            {
              "name": "path",
              "annotation": "PurePath"
            }
          ],
          "return_annotation": "EntryKind"
        },
        {
          "name": "readlink_bytes",
          "parameters": [
            {
              "name": "path",
              "annotation": "PurePath"
            }
          ],
          "return_annotation": "bytes"
        },
        {
          "name": "read_file_bytes",
          "parameters": [
            {
              "name": "path",
              "annotation": "PurePath"
            }
          ],
          "return_annotation": "bytes"
        },
        {
          "name": "path_exists",
          "parameters": [
            {
              "name": "path",
              "annotation": "PurePath"
            }
          ],
          "return_annotation": "bool"
        }
      ],
      "classification": "PROTOCOL"
    }
  ]
}''')


# Successor Task-9 downstream compatibility contract (spec §9, §3, Task-10).
# This is explicit plan-owned truth; implementation output must not generate it.
INTERFACE_MANIFEST["successor_task10_compatibility"] = {
    "changed_downstream_tasks": (10, 11, 12, 13, 14, 16),
    "task15_behavior_delta": None,
    "s9_inventory": (
        ("executable_code_region", "executable-code-region.bin"),
        ("info_plist", "Info.plist"),
        ("code_resources", "CodeResources"),
        ("superblob_index", "superblob-index.bin"),
        ("code_directory", "CodeDirectory"),
        ("entitlements_blob", "Entitlements.blob"),
        ("der_entitlements_blob", "DER-Entitlements.blob"),
        ("identity", "identity.json"),
    ),
}


# ---------------------------------------------------------------------------
# Task-3 protocol-shape test support (V7 §5.4 / §6).  The frozen blob above is
# the plan truth and is never edited to match implementation output.
# ---------------------------------------------------------------------------
import inspect as _inspect
from dataclasses import dataclass as _dataclass

from gate0.feasibility.macos_stage_b_evidence_constants import TestContractError

_PRODUCTION_MODULE_PREFIX = "gate0.feasibility."


@_dataclass(frozen=True)
class ExpectedParameter:
    name: "str"
    annotation: "str"


@_dataclass(frozen=True)
class ExpectedProtocolMethod:
    name: "str"
    parameters: "tuple[ExpectedParameter, ...]"
    return_annotation: "str"


@_dataclass(frozen=True)
class ExpectedProtocol:
    module: "str"
    name: "str"
    classification: "Literal['PROTOCOL']"
    methods: "tuple[ExpectedProtocolMethod, ...]"
    visibility: "Literal['PUBLIC','PRIVATE_SECURITY','TEST_SUPPORT']"


def _manifest_module_name(module_name: str) -> str:
    """Normalize live ``__module__`` to the manifest's module naming convention."""
    if module_name.startswith(_PRODUCTION_MODULE_PREFIX):
        return module_name[len(_PRODUCTION_MODULE_PREFIX):]
    return module_name


def _annotation_text(annotation) -> str:
    if annotation is _inspect.Signature.empty:
        return "None"
    if isinstance(annotation, str):
        return annotation
    return getattr(annotation, "__name__", None) or str(annotation)


def exact_protocol_shape(protocol_type: type) -> ExpectedProtocol:
    """Introspect a live ``typing.Protocol`` class into exact manifest shape truth."""
    if getattr(protocol_type, "_is_protocol", False) is not True:
        raise TestContractError(f"not a Protocol type: {protocol_type!r}")
    methods = []
    for name, member in vars(protocol_type).items():
        if name.startswith("_") or not callable(member):
            continue
        signature = _inspect.signature(member)
        parameters = tuple(
            ExpectedParameter(parameter_name, _annotation_text(parameter.annotation))
            for parameter_name, parameter in signature.parameters.items()
            if parameter_name != "self"
        )
        methods.append(ExpectedProtocolMethod(
            name, parameters, _annotation_text(signature.return_annotation),
        ))
    name = protocol_type.__qualname__
    return ExpectedProtocol(
        module=_manifest_module_name(protocol_type.__module__),
        name=name,
        classification="PROTOCOL",
        methods=tuple(methods),
        visibility="PUBLIC" if not name.startswith("_") else "PRIVATE_SECURITY",
    )


def expected_protocol_from_plan_row(row) -> ExpectedProtocol:
    """Build the frozen comparison truth for one plan §5.4 protocol row."""
    if not isinstance(row, dict) or row.get("classification") != "PROTOCOL":
        raise TestContractError("plan row is not a PROTOCOL row")
    methods = tuple(
        ExpectedProtocolMethod(
            method["name"],
            tuple(ExpectedParameter(p["name"], p["annotation"]) for p in method["parameters"]),
            method["return_annotation"],
        )
        for method in row["methods"]
    )
    return ExpectedProtocol(
        module=row["module"],
        name=row["name"],
        classification="PROTOCOL",
        methods=methods,
        visibility=row["visibility"],
    )
