#!/usr/bin/env python3
"""Shared readiness checker for plugins and modules."""

import sys
from pathlib import Path
from typing import List

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent))
from readiness_base import ReadinessChecker


def create_plugin_checker(plugin_dir: Path, plugin_name: str) -> ReadinessChecker:
    """Create readiness checker for a plugin."""
    checker = ReadinessChecker(f"{plugin_name.upper()} Plugin", plugin_dir)
    
    def check_manifest():
        manifest_file = plugin_dir / "manifest.yaml"
        required_fields = ["name", "version", "plugin_class"]
        passed, message = checker.check_yaml_file(manifest_file, required_fields)
        if not passed:
            return passed, message
        
        # Additional plugin-specific validation
        try:
            import yaml
            with open(manifest_file, 'r') as f:
                manifest = yaml.safe_load(f)
            
            plugin_class = manifest.get("plugin_class", "")
            if ":" not in plugin_class:
                return False, "plugin_class must be in format 'module:ClassName'"
            
            return True, f"Manifest valid (name: {manifest['name']}, version: {manifest['version']})"
        except Exception as e:
            return False, f"Error validating manifest: {e}"
    
    def check_plugin_file():
        try:
            import yaml
            with open(plugin_dir / "manifest.yaml", 'r') as f:
                manifest = yaml.safe_load(f)
            
            plugin_class = manifest.get("plugin_class", "")
            module_name, class_name = plugin_class.split(":", 1)
            plugin_file = plugin_dir / f"{module_name}.py"
            
            if not plugin_file.exists():
                return False, f"Plugin file {module_name}.py not found"
            
            # Try basic import test
            sys.path.insert(0, str(plugin_dir))
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                if spec is None or spec.loader is None:
                    return False, f"Could not load module spec for {module_name}"
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if not hasattr(module, class_name):
                    return False, f"Class {class_name} not found in {module_name}.py"
                
                return True, "Plugin file valid and importable"
            finally:
                sys.path.remove(str(plugin_dir))
                
        except Exception as e:
            return False, f"Error validating plugin file: {e}"
    
    def check_orchestrator_api():
        return checker.check_import("lab_orchestrator.plugin_api", "lab_orchestrator")
    
    checker.add_check("Manifest", check_manifest)
    checker.add_check("Plugin File", check_plugin_file)
    checker.add_check("Orchestrator API", check_orchestrator_api)
    
    return checker


def create_module_checker(module_dir: Path, module_name: str) -> ReadinessChecker:
    """Create readiness checker for a module."""
    checker = ReadinessChecker(f"{module_name.upper()} Module", module_dir)
    
    def check_manifest():
        manifest_file = module_dir / "manifest.yaml"
        required_fields = ["name", "version", "module_file", "class_name"]
        passed, message = checker.check_yaml_file(manifest_file, required_fields)
        if not passed:
            return passed, message
        
        # Additional module-specific validation
        try:
            import yaml
            with open(manifest_file, 'r') as f:
                manifest = yaml.safe_load(f)
            
            # Check if actions are properly defined
            actions = manifest.get("actions", [])
            if not isinstance(actions, list):
                return False, "actions must be a list"
            
            for i, action in enumerate(actions):
                if not isinstance(action, dict) or "name" not in action:
                    return False, f"Action {i} must be a dictionary with 'name' field"
            
            return True, f"Manifest valid ({len(actions)} actions defined)"
        except Exception as e:
            return False, f"Error validating manifest: {e}"
    
    def check_module_file():
        try:
            import yaml
            with open(module_dir / "manifest.yaml", 'r') as f:
                manifest = yaml.safe_load(f)
            
            module_file = manifest.get("module_file", "")
            class_name = manifest.get("class_name", "")
            module_path = module_dir / module_file
            
            if not module_path.exists():
                return False, f"Module file {module_file} not found"
            
            # Try basic import test
            sys.path.insert(0, str(module_dir))
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("module_test", module_path)
                if spec is None or spec.loader is None:
                    return False, f"Could not load module spec for {module_file}"
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if not hasattr(module, class_name):
                    return False, f"Class {class_name} not found in {module_file}"
                
                return True, "Module file valid and importable"
            finally:
                sys.path.remove(str(module_dir))
                
        except Exception as e:
            return False, f"Error validating module file: {e}"
    
    def check_agent_api():
        return checker.check_import("lab_agent.base", "lab_agent")
    
    checker.add_check("Manifest", check_manifest)
    checker.add_check("Module File", check_module_file)
    checker.add_check("Agent API", check_agent_api)
    
    return checker
