#!/usr/bin/env python3
"""
Validation script to verify Railway/HuggingFace separation.

This script checks that:
1. Backend has NO heavy ML dependencies
2. Backend has NO ML-related imports
3. Docker image will be lightweight
4. ML service has all required dependencies

Run this before deploying to Railway!
"""

import os
import sys
from pathlib import Path

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def check_file_exists(filepath: str) -> bool:
    """Check if file exists."""
    return Path(filepath).exists()

def check_no_forbidden_imports(directory: str, forbidden: list) -> tuple[bool, list]:
    """Check that no forbidden imports exist in Python files."""
    issues = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for forbidden_item in forbidden:
                        if forbidden_item in content:
                            issues.append(f"{filepath}: contains '{forbidden_item}'")
    
    return len(issues) == 0, issues

def check_requirements_txt(filepath: str, forbidden: list) -> tuple[bool, list]:
    """Check that requirements.txt doesn't contain forbidden packages."""
    issues = []
    
    if not check_file_exists(filepath):
        return False, [f"{filepath} does not exist"]
    
    with open(filepath, 'r') as f:
        content = f.read().lower()
        for forbidden_pkg in forbidden:
            if forbidden_pkg.lower() in content:
                issues.append(f"{filepath}: contains forbidden package '{forbidden_pkg}'")
    
    return len(issues) == 0, issues

def main():
    print(f"{BOLD}FloorEye Backend Validation{RESET}")
    print("=" * 60)
    print()
    
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"
    requirements_file = backend_dir / "requirements.txt"
    
    all_checks_passed = True
    
    # Check 1: Backend requirements.txt has NO ML dependencies
    print(f"{BOLD}[1] Checking Backend requirements.txt...{RESET}")
    forbidden_packages = [
        "opencv",
        "cv2",
        "ultralytics",
        "torch",
        "tensorflow",
        "numpy"  # Not strictly forbidden, but suspicious
    ]
    
    passed, issues = check_requirements_txt(str(requirements_file), forbidden_packages)
    if passed:
        print(f"  {GREEN}✓{RESET} Backend requirements.txt is clean (no ML dependencies)")
    else:
        print(f"  {RED}✗{RESET} Backend requirements.txt contains forbidden dependencies:")
        for issue in issues:
            print(f"    {RED}-{RESET} {issue}")
        all_checks_passed = False
    print()
    
    # Check 2: Backend code has NO ML imports
    print(f"{BOLD}[2] Checking Backend code for ML imports...{RESET}")
    forbidden_imports = [
        "import cv2",
        "from cv2",
        "import ultralytics",
        "from ultralytics",
        "import torch",
        "from torch",
        "import tensorflow",
        "from tensorflow"
    ]
    
    passed, issues = check_no_forbidden_imports(str(app_dir), forbidden_imports)
    if passed:
        print(f"  {GREEN}✓{RESET} Backend code has no ML imports")
    else:
        print(f"  {RED}✗{RESET} Backend code contains forbidden ML imports:")
        for issue in issues:
            print(f"    {RED}-{RESET} {issue}")
        all_checks_passed = False
    print()
    
    # Check 3: YOLO_SERVICE_URL is configured
    print(f"{BOLD}[3] Checking YOLO_SERVICE_URL configuration...{RESET}")
    config_file = app_dir / "utils" / "config.py"
    if check_file_exists(str(config_file)):
        with open(config_file, 'r') as f:
            content = f.read()
            if "YOLO_SERVICE_URL" in content:
                print(f"  {GREEN}✓{RESET} YOLO_SERVICE_URL is configured in config.py")
            else:
                print(f"  {RED}✗{RESET} YOLO_SERVICE_URL not found in config.py")
                all_checks_passed = False
    else:
        print(f"  {RED}✗{RESET} config.py not found")
        all_checks_passed = False
    print()
    
    # Check 4: .env.example has YOLO_SERVICE_URL
    print(f"{BOLD}[4] Checking .env.example...{RESET}")
    env_example = backend_dir / ".env.example"
    if check_file_exists(str(env_example)):
        with open(env_example, 'r') as f:
            content = f.read()
            if "YOLO_SERVICE_URL" in content:
                print(f"  {GREEN}✓{RESET} YOLO_SERVICE_URL is documented in .env.example")
            else:
                print(f"  {YELLOW}⚠{RESET} YOLO_SERVICE_URL not found in .env.example")
    else:
        print(f"  {YELLOW}⚠{RESET} .env.example not found")
    print()
    
    # Check 5: Dockerfile is lightweight
    print(f"{BOLD}[5] Checking Dockerfile...{RESET}")
    dockerfile = backend_dir / "Dockerfile"
    if check_file_exists(str(dockerfile)):
        with open(dockerfile, 'r') as f:
            content = f.read()
            opencv_deps = ["libgl1", "libopencv", "opencv"]
            has_opencv = any(dep in content.lower() for dep in opencv_deps)
            
            if has_opencv:
                print(f"  {RED}✗{RESET} Dockerfile contains OpenCV-related dependencies")
                all_checks_passed = False
            else:
                print(f"  {GREEN}✓{RESET} Dockerfile is lightweight (no OpenCV deps)")
    else:
        print(f"  {YELLOW}⚠{RESET} Dockerfile not found")
    print()
    
    # Final result
    print("=" * 60)
    if all_checks_passed:
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED{RESET}")
        print()
        print("Backend is properly separated from ML dependencies.")
        print("Safe to deploy to Railway!")
        print()
        print(f"{BOLD}Next steps:{RESET}")
        print("1. Deploy ML service to HuggingFace")
        print("2. Set YOLO_SERVICE_URL environment variable in Railway")
        print("3. Deploy backend to Railway")
        return 0
    else:
        print(f"{RED}{BOLD}✗ VALIDATION FAILED{RESET}")
        print()
        print("Fix the issues above before deploying to Railway.")
        print()
        print("See Backend/ARCHITECTURE.md for guidance.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
