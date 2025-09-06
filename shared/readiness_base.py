#!/usr/bin/env python3
"""Base class for readiness checks to reduce code duplication."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Callable, Tuple


class ReadinessChecker:
    """Base class for component readiness checks."""
    
    def __init__(self, component_name: str, component_dir: Path):
        self.component_name = component_name
        self.component_dir = component_dir
        self.checks: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = []
    
    def add_check(self, name: str, check_func: Callable[[], Tuple[bool, str]]) -> None:
        """Add a check function."""
        self.checks.append((name, check_func))
    
    def check_python_version(self, min_version: Tuple[int, int] = (3, 8)) -> Tuple[bool, str]:
        """Check Python version."""
        if sys.version_info < min_version:
            return False, f"Python {min_version[0]}.{min_version[1]}+ required, found {sys.version_info.major}.{sys.version_info.minor}"
        return True, f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def check_file_exists(self, file_path: Path, description: str) -> Tuple[bool, str]:
        """Check if a file exists."""
        if file_path.exists():
            return True, f"{description} found"
        return False, f"{description} missing: {file_path}"
    
    def check_import(self, module_name: str, package_name: str = None) -> Tuple[bool, str]:
        """Check if a module can be imported."""
        try:
            __import__(module_name)
            return True, f"{package_name or module_name} available"
        except ImportError:
            return False, f"{package_name or module_name} not installed"
    
    def check_yaml_file(self, file_path: Path, required_fields: List[str] = None) -> Tuple[bool, str]:
        """Check YAML file validity."""
        if not file_path.exists():
            return False, f"{file_path.name} not found"
        
        try:
            import yaml
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                return False, f"{file_path.name} must contain a dictionary"
            
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return False, f"{file_path.name} missing fields: {', '.join(missing)}"
            
            return True, f"{file_path.name} valid"
            
        except Exception as e:
            return False, f"Error reading {file_path.name}: {e}"
    
    def run_checks(self, verbose: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """Run all registered checks."""
        results = {}
        all_passed = True
        
        for check_name, check_func in self.checks:
            try:
                passed, message = check_func()
                results[check_name] = {
                    "status": "PASS" if passed else "FAIL",
                    "message": message
                }
                
                if not passed:
                    all_passed = False
                    
                if verbose or not passed:
                    status_icon = "✅" if passed else "❌"
                    print(f"{status_icon} {check_name}: {message}")
                    
            except Exception as e:
                results[check_name] = {
                    "status": "ERROR",
                    "message": f"Check failed: {e}"
                }
                all_passed = False
                
                if verbose:
                    print(f"❌ {check_name}: Check failed: {e}")
        
        return all_passed, results
    
    def main(self, suggestions: Dict[str, str] = None) -> None:
        """Main entry point with argument parsing."""
        parser = argparse.ArgumentParser(description=f"Check {self.component_name} readiness")
        parser.add_argument("--verbose", action="store_true", help="Show detailed output")
        parser.add_argument("--json", action="store_true", help="Output results as JSON")
        parser.add_argument("--fix", action="store_true", help="Attempt to fix issues (not implemented)")
        
        args = parser.parse_args()
        
        if not args.verbose and not args.json:
            print(f"{self.component_name} - Readiness Check")
            print("=" * (len(self.component_name) + 18))
        
        all_passed, results = self.run_checks(args.verbose)
        
        if args.json:
            output = {
                "overall_status": "PASS" if all_passed else "FAIL",
                "checks": results,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            print(json.dumps(output, indent=2))
        else:
            print("\n" + "=" * (len(self.component_name) + 18))
            if all_passed:
                print("✅ OVERALL STATUS: READY")
                print(f"{self.component_name} is properly configured and ready to run.")
            else:
                print("❌ OVERALL STATUS: NOT READY")
                print(f"Please fix the issues above before running {self.component_name.lower()}.")
                
                # Show suggestions
                if suggestions:
                    failed_checks = [name for name, result in results.items() if result["status"] == "FAIL"]
                    for check_name in failed_checks:
                        if check_name in suggestions:
                            print(f"\nSuggestion: {suggestions[check_name]}")
        
        sys.exit(0 if all_passed else 1)
