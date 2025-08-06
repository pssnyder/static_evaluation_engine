#!/usr/bin/env python3
"""
Data Extraction Script for Chess Engine Analysis Dashboard

This script parses the evaluation.py file and other engine components
to extract configuration data, PST tables, weights, and metrics for
the analysis dashboard.

Usage: python extract_engine_data.py
Output: JSON files in the results/analysis/ directory
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the parent directory to path to import engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EngineDataExtractor:
    """Extracts data from engine files for dashboard analysis."""
    
    def __init__(self, engine_root: str):
        self.engine_root = Path(engine_root)
        self.evaluation_file = self.engine_root / "evaluation.py"
        self.engine_file = self.engine_root / "engine.py"
        self.results_dir = self.engine_root / "results"
        self.analysis_dir = self.results_dir / "analysis"
        
        # Ensure analysis directory exists
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_evaluation_data(self) -> Dict[str, Any]:
        """Extract PST tables, weights, and piece values from evaluation.py."""
        if not self.evaluation_file.exists():
            raise FileNotFoundError(f"evaluation.py not found at {self.evaluation_file}")
        
        with open(self.evaluation_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse as AST for robust extraction
        tree = ast.parse(content)
        
        evaluation_data = {
            "piece_values": {},
            "weights": {},
            "pattern_bonuses": {},
            "pst_tables": {},
            "config": {},
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Extract class definition and analyze
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Evaluation":
                self._extract_from_class(node, evaluation_data)
        
        return evaluation_data
    
    def _extract_from_class(self, class_node: ast.ClassDef, data: Dict[str, Any]):
        """Extract data from the Evaluation class."""
        
        # Look for class variables and method assignments
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                self._extract_assignment(node, data)
            elif isinstance(node, ast.FunctionDef):
                if node.name == "__init__":
                    self._extract_init_method(node, data)
                elif node.name == "init_piece_square_tables":
                    self._extract_pst_method(node, data)
    
    def _extract_assignment(self, assign_node: ast.Assign, data: Dict[str, Any]):
        """Extract data from assignment statements."""
        if len(assign_node.targets) == 1:
            target = assign_node.targets[0]
            
            # Extract PIECE_VALUES
            if isinstance(target, ast.Name) and target.id == "PIECE_VALUES":
                if isinstance(assign_node.value, ast.Dict):
                    data["piece_values"] = self._extract_dict_values(assign_node.value)
    
    def _extract_init_method(self, init_node: ast.FunctionDef, data: Dict[str, Any]):
        """Extract weights and config from __init__ method."""
        for node in ast.walk(init_node):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1:
                    target = node.targets[0]
                    
                    # Extract weights
                    if (isinstance(target, ast.Attribute) and 
                        target.attr == "weights" and
                        isinstance(node.value, ast.Call)):
                        
                        # Look for get method with default dict
                        if (isinstance(node.value.func, ast.Attribute) and
                            node.value.func.attr == "get" and
                            len(node.value.args) >= 2):
                            
                            default_dict = node.value.args[1]
                            if isinstance(default_dict, ast.Dict):
                                data["weights"] = self._extract_dict_values(default_dict)
                    
                    # Extract pattern bonuses
                    elif (isinstance(target, ast.Attribute) and 
                          target.attr == "pattern_bonuses" and
                          isinstance(node.value, ast.Call)):
                        
                        if (isinstance(node.value.func, ast.Attribute) and
                            node.value.func.attr == "get" and
                            len(node.value.args) >= 2):
                            
                            default_dict = node.value.args[1]
                            if isinstance(default_dict, ast.Dict):
                                data["pattern_bonuses"] = self._extract_dict_values(default_dict)
    
    def _extract_pst_method(self, pst_node: ast.FunctionDef, data: Dict[str, Any]):
        """Extract PST tables from init_piece_square_tables method."""
        pst_tables = {}
        
        for node in ast.walk(pst_node):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1:
                    target = node.targets[0]
                    
                    if (isinstance(target, ast.Attribute) and
                        target.attr.endswith('_table') and
                        isinstance(node.value, ast.List)):
                        
                        table_name = target.attr.replace('_table', '')
                        table_values = self._extract_list_values(node.value)
                        if table_values:
                            pst_tables[table_name] = table_values
        
        data["pst_tables"] = pst_tables
    
    def _extract_dict_values(self, dict_node: ast.Dict) -> Dict[str, Any]:
        """Extract values from AST Dict node."""
        result = {}
        
        for key, value in zip(dict_node.keys, dict_node.values):
            if isinstance(key, ast.Constant):
                key_str = str(key.value)
            elif isinstance(key, ast.Str):
                key_str = key.s
            elif isinstance(key, ast.Attribute):
                # Handle chess.PAWN etc.
                key_str = key.attr.lower()
            else:
                continue
            
            if isinstance(value, ast.Constant):
                result[key_str] = value.value
            elif isinstance(value, ast.Num):
                result[key_str] = value.n
            elif isinstance(value, ast.Str):
                result[key_str] = value.s
        
        return result
    
    def _extract_list_values(self, list_node: ast.List) -> List[int]:
        """Extract integer values from AST List node."""
        values = []
        
        for item in list_node.elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, (int, float)):
                values.append(int(item.value))
            elif hasattr(item, 'n'):  # ast.Num for older Python versions
                try:
                    values.append(int(getattr(item, 'n')))
                except (ValueError, TypeError):
                    pass
            elif isinstance(item, ast.UnaryOp) and isinstance(item.op, ast.USub):
                if isinstance(item.operand, ast.Constant) and isinstance(item.operand.value, (int, float)):
                    values.append(-int(item.operand.value))
                elif hasattr(item.operand, 'n'):
                    try:
                        values.append(-int(getattr(item.operand, 'n')))
                    except (ValueError, TypeError):
                        pass
        
        return values
    
    def extract_code_statistics(self) -> Dict[str, Any]:
        """Extract code statistics from engine files."""
        stats = {
            "files_analyzed": [],
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "evaluation_functions": [],
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Analyze key engine files
        files_to_analyze = [
            "evaluation.py",
            "engine.py", 
            "uci_interface.py",
            "data_collector.py"
        ]
        
        for filename in files_to_analyze:
            filepath = self.engine_root / filename
            if filepath.exists():
                file_stats = self._analyze_file(filepath)
                stats["files_analyzed"].append(file_stats)
                stats["total_lines"] += file_stats["lines"]
                stats["total_functions"] += file_stats["functions"]
                stats["total_classes"] += file_stats["classes"]
                
                # Special handling for evaluation.py
                if filename == "evaluation.py":
                    stats["evaluation_functions"] = file_stats["method_names"]
        
        return stats
    
    def _analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single Python file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                "filename": filepath.name,
                "lines": len(content.splitlines()),
                "functions": 0,
                "classes": 0,
                "method_names": [],
                "error": "Syntax error in file"
            }
        
        functions = []
        classes = []
        method_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                if node.name.startswith('evaluate_'):
                    method_names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return {
            "filename": filepath.name,
            "lines": len(content.splitlines()),
            "functions": len(functions),
            "classes": len(classes),
            "function_names": functions,
            "class_names": classes,
            "method_names": method_names
        }
    
    def load_puzzle_data(self, csv_path: Optional[str] = None) -> Dict[str, Any]:
        """Load and analyze puzzle data for filtering options."""
        if csv_path is None:
            csv_path = str(self.engine_root / "testing" / "lichess_db_puzzle.csv")
        
        puzzle_data = {
            "total_puzzles": 0,
            "rating_range": {"min": 800, "max": 2800},
            "available_themes": [],
            "solution_lengths": [],
            "sample_puzzles": [],
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        if not os.path.exists(csv_path):
            puzzle_data["error"] = f"Puzzle CSV not found at {csv_path}"
            return puzzle_data
        
        # Analyze CSV structure (first 1000 lines for speed)
        import csv
        themes_set = set()
        lengths_set = set()
        ratings = []
        sample_count = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                
                for i, row in enumerate(reader):
                    if i >= 1000:  # Limit analysis for speed
                        break
                    
                    if len(row) >= 8:
                        # Extract rating
                        try:
                            rating = int(row[3]) if row[3].isdigit() else 0
                            if rating > 0:
                                ratings.append(rating)
                        except (ValueError, IndexError):
                            pass
                        
                        # Extract themes
                        try:
                            themes = row[7].split()
                            themes_set.update(themes)
                        except IndexError:
                            pass
                        
                        # Extract solution length
                        try:
                            moves = row[2].split()
                            lengths_set.add(len(moves))
                        except IndexError:
                            pass
                        
                        # Sample puzzles for testing
                        if sample_count < 10:
                            puzzle_data["sample_puzzles"].append({
                                "id": row[0],
                                "fen": row[1],
                                "moves": row[2].split(),
                                "rating": rating,
                                "themes": themes
                            })
                            sample_count += 1
                
                puzzle_data["total_puzzles"] = i + 1
                if ratings:
                    puzzle_data["rating_range"] = {
                        "min": min(ratings),
                        "max": max(ratings)
                    }
                puzzle_data["available_themes"] = sorted(list(themes_set))
                puzzle_data["solution_lengths"] = sorted(list(lengths_set))
                
        except Exception as e:
            puzzle_data["error"] = f"Error reading CSV: {str(e)}"
        
        return puzzle_data
    
    def generate_analysis_data(self):
        """Generate all analysis data files."""
        print("🔍 Extracting engine evaluation data...")
        eval_data = self.extract_evaluation_data()
        
        print("📊 Analyzing code statistics...")
        code_stats = self.extract_code_statistics()
        
        print("🧩 Loading puzzle data...")
        puzzle_data = self.load_puzzle_data()
        
        # Save individual data files
        files_created = []
        
        # Evaluation configuration
        eval_file = self.analysis_dir / "evaluation_config.json"
        with open(eval_file, 'w') as f:
            json.dump(eval_data, f, indent=2)
        files_created.append(eval_file)
        
        # Code statistics
        stats_file = self.analysis_dir / "code_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(code_stats, f, indent=2)
        files_created.append(stats_file)
        
        # Puzzle metadata
        puzzle_file = self.analysis_dir / "puzzle_metadata.json"
        with open(puzzle_file, 'w') as f:
            json.dump(puzzle_data, f, indent=2)
        files_created.append(puzzle_file)
        
        # Combined dashboard data
        dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "evaluation": eval_data,
            "statistics": code_stats,
            "puzzles": puzzle_data
        }
        
        dashboard_file = self.analysis_dir / "dashboard_data.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        files_created.append(dashboard_file)
        
        print(f"✅ Generated {len(files_created)} analysis files:")
        for file_path in files_created:
            print(f"   📄 {file_path}")
        
        return dashboard_data

def main():
    """Main execution function."""
    # Determine engine root directory
    script_dir = Path(__file__).parent
    engine_root = script_dir.parent
    
    print(f"🚀 Chess Engine Data Extraction")
    print(f"Engine Root: {engine_root}")
    print("=" * 50)
    
    try:
        extractor = EngineDataExtractor(str(engine_root))
        data = extractor.generate_analysis_data()
        
        print("\n🎉 Data extraction completed successfully!")
        print(f"📊 Analysis data available in: {extractor.analysis_dir}")
        
        # Print summary
        eval_data = data["evaluation"]
        stats_data = data["statistics"]
        puzzle_data = data["puzzles"]
        
        print(f"\n📈 Summary:")
        print(f"   PST Tables: {len(eval_data['pst_tables'])}")
        print(f"   Evaluation Weights: {len(eval_data['weights'])}")
        print(f"   Total Code Lines: {stats_data['total_lines']}")
        print(f"   Available Themes: {len(puzzle_data['available_themes'])}")
        print(f"   Puzzle Rating Range: {puzzle_data['rating_range']['min']}-{puzzle_data['rating_range']['max']}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
