import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, project_root)

from tests.test_detector import test_detect_notion_upsell, test_detect_directive_hijack, test_clean_text_passes
from tests.test_sanitizer import test_strip_banned_guidance_keys, test_redact_upsell_in_strings
from tests.test_coercer import test_coerce_paywall_disguised_error, test_ignore_normal_errors
from tests.test_telemetry import test_telemetry_reduction_calculation

def run():
    tests = [
        ("test_detect_notion_upsell", test_detect_notion_upsell),
        ("test_detect_directive_hijack", test_detect_directive_hijack),
        ("test_clean_text_passes", test_clean_text_passes),
        ("test_strip_banned_guidance_keys", test_strip_banned_guidance_keys),
        ("test_redact_upsell_in_strings", test_redact_upsell_in_strings),
        ("test_coerce_paywall_disguised_error", test_coerce_paywall_disguised_error),
        ("test_ignore_normal_errors", test_ignore_normal_errors),
        ("test_telemetry_reduction_calculation", test_telemetry_reduction_calculation),
    ]

    print("==================================================")
    print("      RUNNING MCP ZERO-TRUST FIREWALL TESTS       ")
    print("==================================================")
    passed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"  ✓ {name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"  ✗ {name}: FAILED -> {e}")
            sys.exit(1)

    print("--------------------------------------------------")
    print(f"Result: {passed}/{len(tests)} tests passed (100% SUCCESS)")
    print("==================================================")

if __name__ == "__main__":
    run()
