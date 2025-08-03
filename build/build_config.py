#!/usr/bin/env python3
"""
Build Configuration for Cece (Static Evaluation Chess Engine)

Centralized configuration for build process to avoid manual edits.
"""

import time
from datetime import datetime

# =============================================================================
# BUILD CONFIGURATION
# =============================================================================

BUILD_CONFIG = {
    # Version Information
    'version': '1.0',
    'variant': 'RELEASE',  # RELEASE, BETA, ALPHA, STABLE, etc.
    'engine_name': 'Cece - Static Evaluation Chess Engine',
    'short_name': 'Cece',
    
    # Build Settings
    'executable_name': 'Cece_v1.0',
    'tournament_folder': 'Cece_v1.0_Tournament',
    
    # Features Description
    'features': [
        'Hybrid Architecture (python-chess + custom evaluation)',
        'Advanced Static Evaluation',
        'Custom Pattern Recognition',
        'Comprehensive Data Collection',
        'Real-Time Parameter Tuning',
        'Professional UCI Interface',
        'Tournament Ready',
        'Research & Analysis Tools'
    ],
    
    # Engine Information
    'author': 'Your Name',
    'description': 'Minimalist chess engine focusing on evaluation excellence',
    'attribution': 'Built on python-chess by Niklas Fiekas',
    'license': 'GPL-3.0'
}

def get_build_info():
    """Get dynamic build information for current build."""
    config = BUILD_CONFIG.copy()
    
    # Generate dynamic strings
    config['version_string'] = f"v{config['version']}"
    if config['variant'] != 'RELEASE':
        config['version_string'] += f"_{config['variant']}"
    
    config['full_name'] = f"{config['short_name']} {config['version_string']}"
    config['executable_name'] = f"{config['executable_name']}.exe"
    
    # Build timestamp
    config['build_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config['build_date'] = datetime.now().strftime("%Y%m%d")
    
    # Feature summary
    config['feature_summary'] = ', '.join(config['features'][:3]) + f" (+{len(config['features'])-3} more)"
    
    return config

def get_version_info():
    """Get version information for file versioning."""
    config = BUILD_CONFIG
    return {
        'version': config['version'],
        'variant': config['variant'],
        'full_version': f"{config['version']}.{config['variant']}"
    }

def get_engine_metadata():
    """Get engine metadata for UCI and documentation."""
    config = BUILD_CONFIG
    return {
        'name': config['engine_name'],
        'author': config['author'],
        'version': config['version'],
        'description': config['description'],
        'features': config['features'],
        'attribution': config['attribution'],
        'license': config['license']
    }

if __name__ == "__main__":
    """Test the build configuration."""
    print("Cece Build Configuration Test")
    print("=" * 40)
    
    build_info = get_build_info()
    print(f"Engine: {build_info['full_name']}")
    print(f"Executable: {build_info['executable_name']}")
    print(f"Features: {build_info['feature_summary']}")
    print(f"Build Time: {build_info['build_timestamp']}")
    
    print("\nVersion Info:")
    version_info = get_version_info()
    for key, value in version_info.items():
        print(f"  {key}: {value}")
    
    print("\nEngine Metadata:")
    metadata = get_engine_metadata()
    for key, value in metadata.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
