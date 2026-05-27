#!/usr/bin/env python3
"""
Test email validation for student signup
"""

import re

# Frontend validation regex
regex = r'^[a-zA-Z0-9._-]+@jainuniversity\.ac\.in$'

# Test email
test_email = "mili.25008261@jainuniversity.ac.in"

print("=" * 60)
print("Email Validation Test")
print("=" * 60)
print(f"Email to test: {test_email}")
print(f"Regex pattern: {regex}")
print()

# Test the email
result = re.match(regex, test_email)

if result:
    print("[OK] Email is VALID and will be ACCEPTED")
    print(f"Matched: {result.group()}")
else:
    print("[FAIL] Email is INVALID and will be REJECTED")
    print("Reason: Does not match the required pattern")

print()
print("Pattern breakdown:")
print("  - Allowed characters before @: a-z, A-Z, 0-9, ., _, -")
print("  - Required domain: @jainuniversity.ac.in")
print()

# Test a few more examples
test_emails = [
    "mili.25008261@jainuniversity.ac.in",
    "john.doe@jainuniversity.ac.in",
    "student_123@jainuniversity.ac.in",
    "test-email@jainuniversity.ac.in",
    "invalid@example.com",
    "test@jainuniversity.ac.in",
]

print("Testing multiple email formats:")
print("-" * 60)
for email in test_emails:
    is_valid = re.match(regex, email) is not None
    status = "[OK]" if is_valid else "[FAIL]"
    print(f"{status} {email}")

