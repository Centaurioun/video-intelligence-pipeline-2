"""Independent expectations for the generated three-arm compatibility slice."""

ARMS = ("VIP_V1_BASE", "VIP_V2_BASE", "VIP_V2_SO400M")
PAIR_ORDER = ((ARMS[0], ARMS[1]), (ARMS[0], ARMS[2]), (ARMS[1], ARMS[2]))
B07_MARKERS = (
    {"metric_id": "recall_at_5", "status": "NOT_COMPUTABLE", "reason": "POOLED_GROUND_TRUTH"},
    {"metric_id": "ndcg_at_10", "status": "NOT_COMPUTABLE", "reason": "METRIC_NOT_IMPLEMENTED"},
)

EXPECTED_CASES = {
    "positive_one_axis": {
        "statuses": ("PASS", "PASS", "FAIL"),
        "failure_classes": (None, None, "QUALITY"),
        "primary_values": (1.0, 1.0, 0.0),
    },
    "partial_coverage": {
        "statuses": ("FAIL", "FAIL", "FAIL"),
        "failure_classes": ("COVERAGE_INCOMPLETE", "COVERAGE_INCOMPLETE", "COVERAGE_INCOMPLETE"),
        "primary_values": (1.0, 1.0, 0.0),
    },
    "tie_no_superiority": {
        "statuses": ("FAIL", "FAIL", "FAIL"),
        "failure_classes": ("QUALITY", "QUALITY", "QUALITY"),
        "primary_values": (0.0, 0.0, 0.0),
    },
    "quality_failure": {
        "statuses": ("FAIL", "FAIL", "FAIL"),
        "failure_classes": ("QUALITY", "QUALITY", "QUALITY"),
        "primary_values": (0.0, 0.0, 0.0),
    },
    "resource_failure": {
        "statuses": ("FAIL", "FAIL", "FAIL"),
        "failure_classes": (
            "RESOURCE_OPERABILITY", "RESOURCE_OPERABILITY", "RESOURCE_OPERABILITY"
        ),
        "primary_values": (1.0, 1.0, 0.0),
    },
}
