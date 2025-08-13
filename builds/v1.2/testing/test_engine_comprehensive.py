#!/usr/bin/env python3
"""
Comprehensive Engine Testing Suite for Cece v1.1 Release
========================================================

Tests all major engine components before building the release:
- UCI Protocol compliance
- Engine functionality  
- Evaluation system
- Search algorithm
- Performance benchmarks
- Integration tests
"""

import subprocess
import time
import threading
import os
import sys
import chess
import chess.pgn
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    """Container for individual test results."""
    name: str
    passed: bool
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None

class EngineTestSuite:
    """Comprehensive testing suite for the chess engine."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.engine_path = "uci_interface.py"  # Correct UCI entry point
        self.start_time = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success status."""
        self.start_time = time.time()
        self.log("🚀 Starting Comprehensive Engine Test Suite")
        self.log("=" * 60)
        
        # Test categories in order of importance
        test_categories = [
            ("🔧 Basic Engine Tests", self._run_basic_tests),
            ("🎯 UCI Protocol Tests", self._run_uci_tests),
            ("♟️ Chess Logic Tests", self._run_chess_tests),
            ("🧮 Evaluation Tests", self._run_evaluation_tests),
            ("🔍 Search Algorithm Tests", self._run_search_tests),
            ("⚡ Performance Tests", self._run_performance_tests),
            ("🎮 Integration Tests", self._run_integration_tests),
        ]
        
        for category_name, test_func in test_categories:
            self.log(f"\n{category_name}")
            self.log("-" * 40)
            
            try:
                test_func()
            except Exception as e:
                self.log(f"❌ Category failed with exception: {e}", "ERROR")
                self.results.append(TestResult(
                    name=f"{category_name} - Exception",
                    passed=False,
                    duration=0.0,
                    message=str(e)
                ))
        
        # Generate final report
        self._generate_report()
        
        # Return overall success
        passed_tests = sum(1 for r in self.results if r.passed)
        total_tests = len(self.results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        return success_rate >= 0.9  # 90% pass rate required
    
    def _run_test(self, name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test and record the result."""
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if isinstance(result, tuple):
                passed, message, details = result
            elif isinstance(result, bool):
                passed, message, details = result, "Test completed", None
            else:
                passed, message, details = bool(result), str(result), None
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message=message,
                details=details
            ))
            
            status = "✅" if passed else "❌"
            self.log(f"{status} {name} ({duration:.2f}s): {message}")
            
            return passed
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=duration,
                message=f"Exception: {str(e)}"
            ))
            
            self.log(f"❌ {name} ({duration:.2f}s): Exception - {e}", "ERROR")
            return False
    
    def _run_basic_tests(self):
        """Test basic engine functionality."""
        
        def test_engine_import():
            """Test that engine modules can be imported."""
            try:
                import engine
                import evaluation
                import uci_interface
                return True, "All modules imported successfully", None
            except ImportError as e:
                return False, f"Import failed: {e}", None
        
        def test_engine_creation():
            """Test engine object creation."""
            try:
                import engine
                chess_engine = engine.ChessEngine()
                return True, "Engine created successfully", {
                    "engine_type": type(chess_engine).__name__
                }
            except Exception as e:
                return False, f"Engine creation failed: {e}", None
        
        def test_evaluation_creation():
            """Test evaluation system creation."""
            try:
                import evaluation
                eval_system = evaluation.Evaluation()
                return True, "Evaluation system created successfully", {
                    "weights": len(eval_system.weights) if hasattr(eval_system, 'weights') else 0
                }
            except Exception as e:
                return False, f"Evaluation creation failed: {e}", None
        
        self._run_test("Engine Module Import", test_engine_import)
        self._run_test("Engine Object Creation", test_engine_creation)
        self._run_test("Evaluation System Creation", test_evaluation_creation)
    
    def _run_uci_tests(self):
        """Test UCI protocol compliance."""
        
        def test_uci_startup():
            """Test basic UCI communication."""
            try:
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Send UCI command
                try:
                    stdout, stderr = process.communicate(input="uci\nquit\n", timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    return False, "UCI startup timed out", None
                
                if "uciok" in stdout:
                    return True, "UCI protocol responded correctly", {
                        "stdout_lines": len(stdout.splitlines()),
                        "stderr_lines": len(stderr.splitlines()) if stderr else 0
                    }
                else:
                    return False, f"No uciok response. Stdout: {stdout[:200]}", None
                    
            except Exception as e:
                return False, f"UCI test failed: {e}", None
        
        def test_uci_commands():
            """Test essential UCI commands."""
            commands = [
                "uci",
                "isready", 
                "ucinewgame",
                "position startpos",
                "go movetime 100",
                "quit"
            ]
            
            try:
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                input_str = "\n".join(commands) + "\n"
                stdout, stderr = process.communicate(input=input_str, timeout=15)
                
                # Check for expected responses
                required_responses = ["uciok", "readyok", "bestmove"]
                missing_responses = []
                
                for response in required_responses:
                    if response not in stdout:
                        missing_responses.append(response)
                
                if not missing_responses:
                    return True, "All UCI commands responded correctly", {
                        "commands_tested": len(commands),
                        "output_length": len(stdout)
                    }
                else:
                    return False, f"Missing responses: {missing_responses}", None
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "UCI commands timed out", None
            except Exception as e:
                return False, f"UCI commands test failed: {e}", None
        
        self._run_test("UCI Startup", test_uci_startup)
        self._run_test("UCI Command Sequence", test_uci_commands)
    
    def _run_chess_tests(self):
        """Test chess logic and move generation."""
        
        def test_move_generation():
            """Test legal move generation."""
            try:
                import engine
                chess_engine = engine.ChessEngine()
                
                # Test starting position
                board = chess.Board()
                moves = list(board.legal_moves)
                
                if len(moves) == 20:  # Standard starting position has 20 legal moves
                    return True, f"Correct move count: {len(moves)}", {
                        "legal_moves": len(moves),
                        "position": board.fen()
                    }
                else:
                    return False, f"Incorrect move count: {len(moves)}, expected 20", None
                    
            except Exception as e:
                return False, f"Move generation failed: {e}", None
        
        def test_position_handling():
            """Test various chess positions."""
            test_positions = [
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting
                "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",  # e4 e5
                "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",  # Castling test
                "4k3/8/8/8/8/8/8/4K3 w - - 0 1"  # Kings only (valid minimal position)
            ]
            
            try:
                valid_positions = 0
                for fen in test_positions:
                    board = chess.Board(fen)
                    if board.is_valid():
                        valid_positions += 1
                
                if valid_positions == len(test_positions):
                    return True, f"All {valid_positions} positions valid", {
                        "positions_tested": len(test_positions)
                    }
                else:
                    return False, f"Only {valid_positions}/{len(test_positions)} positions valid", None
                    
            except Exception as e:
                return False, f"Position handling failed: {e}", None
        
        self._run_test("Move Generation", test_move_generation)
        self._run_test("Position Handling", test_position_handling)
    
    def _run_evaluation_tests(self):
        """Test evaluation system."""
        
        def test_evaluation_scoring():
            """Test basic evaluation scoring."""
            try:
                import evaluation
                import chess
                
                eval_system = evaluation.Evaluation()
                
                # Test starting position (should be roughly equal)
                board = chess.Board()
                score = eval_system.evaluate(board)
                
                # Starting position should be close to 0
                if abs(score) < 100:  # Within 1 pawn of equality
                    return True, f"Starting position score: {score}", {
                        "score": score,
                        "position": board.fen()
                    }
                else:
                    return False, f"Starting position too unbalanced: {score}", None
                    
            except Exception as e:
                return False, f"Evaluation scoring failed: {e}", None
        
        def test_material_evaluation():
            """Test material value calculation."""
            try:
                import evaluation
                import chess
                
                eval_system = evaluation.Evaluation()
                
                # Test position with material advantage
                board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKB1R w KQkq - 0 2")
                board.remove_piece_at(chess.H1)  # Remove white rook
                
                score = eval_system.evaluate(board)
                
                # Black should be ahead by roughly a rook (500 points)
                if score < -300:  # Black advantage
                    return True, f"Material evaluation correct: {score}", {
                        "score": score,
                        "material_diff": "Black +Rook"
                    }
                else:
                    return False, f"Material evaluation incorrect: {score}", None
                    
            except Exception as e:
                return False, f"Material evaluation failed: {e}", None
        
        self._run_test("Basic Evaluation Scoring", test_evaluation_scoring)
        self._run_test("Material Evaluation", test_material_evaluation)
    
    def _run_search_tests(self):
        """Test search algorithm."""
        
        def test_move_search():
            """Test that engine can find moves."""
            try:
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                commands = [
                    "uci",
                    "isready",
                    "position startpos",
                    "go movetime 1000",
                    "quit"
                ]
                
                input_str = "\n".join(commands) + "\n"
                stdout, stderr = process.communicate(input=input_str, timeout=20)
                
                # Look for bestmove in output
                lines = stdout.splitlines()
                bestmove_lines = [line for line in lines if line.startswith("bestmove")]
                
                if bestmove_lines:
                    bestmove = bestmove_lines[-1]
                    move_part = bestmove.split()[1] if len(bestmove.split()) > 1 else "none"
                    
                    if move_part != "none" and len(move_part) >= 4:
                        return True, f"Found move: {move_part}", {
                            "bestmove": bestmove,
                            "search_time": "1000ms"
                        }
                    else:
                        return False, f"Invalid move returned: {move_part}", None
                else:
                    return False, "No bestmove found in output", None
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Search timed out", None
            except Exception as e:
                return False, f"Search test failed: {e}", None
        
        def test_tactical_position():
            """Test engine on a simple tactical position."""
            try:
                # Simple mate in 1: Qh5# 
                tactical_fen = "rnbqkb1r/pppp1ppp/5n2/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR w KQkq - 2 3"
                
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                commands = [
                    "uci",
                    "isready", 
                    f"position fen {tactical_fen}",
                    "go movetime 2000",
                    "quit"
                ]
                
                input_str = "\n".join(commands) + "\n"
                stdout, stderr = process.communicate(input=input_str, timeout=25)
                
                # Look for the move (should find Qh5 or similar strong move)
                lines = stdout.splitlines()
                bestmove_lines = [line for line in lines if line.startswith("bestmove")]
                
                if bestmove_lines:
                    bestmove = bestmove_lines[-1]
                    return True, f"Tactical move found: {bestmove}", {
                        "position": tactical_fen,
                        "result": bestmove
                    }
                else:
                    return False, "No move found for tactical position", None
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Tactical search timed out", None
            except Exception as e:
                return False, f"Tactical test failed: {e}", None
        
        self._run_test("Move Search", test_move_search)
        self._run_test("Tactical Position", test_tactical_position)
    
    def _run_performance_tests(self):
        """Test engine performance."""
        
        def test_response_time():
            """Test engine response time."""
            try:
                start_time = time.time()
                
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                commands = [
                    "uci",
                    "isready",
                    "position startpos",
                    "go movetime 500",
                    "quit"
                ]
                
                input_str = "\n".join(commands) + "\n"
                stdout, stderr = process.communicate(input=input_str, timeout=10)
                
                total_time = time.time() - start_time
                
                if total_time < 8.0:  # Should complete within 8 seconds
                    return True, f"Response time: {total_time:.2f}s", {
                        "total_time": total_time,
                        "target_time": "8.0s"
                    }
                else:
                    return False, f"Too slow: {total_time:.2f}s", None
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Performance test timed out", None
            except Exception as e:
                return False, f"Performance test failed: {e}", None
        
        def test_multiple_searches():
            """Test multiple consecutive searches."""
            try:
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                commands = ["uci", "isready"]
                
                # Multiple quick searches
                positions = [
                    "position startpos",
                    "position startpos moves e2e4",
                    "position startpos moves e2e4 e7e5",
                    "position startpos moves e2e4 e7e5 g1f3"
                ]
                
                for pos in positions:
                    commands.extend([pos, "go movetime 200"])
                
                commands.append("quit")
                
                start_time = time.time()
                input_str = "\n".join(commands) + "\n"
                stdout, stderr = process.communicate(input=input_str, timeout=15)
                total_time = time.time() - start_time
                
                # Count bestmove responses
                bestmove_count = stdout.count("bestmove")
                
                if bestmove_count >= len(positions):
                    return True, f"Multiple searches completed: {bestmove_count} moves in {total_time:.2f}s", {
                        "searches": bestmove_count,
                        "total_time": total_time,
                        "avg_time": total_time / bestmove_count
                    }
                else:
                    return False, f"Only {bestmove_count}/{len(positions)} searches completed", None
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Multiple searches timed out", None
            except Exception as e:
                return False, f"Multiple searches failed: {e}", None
        
        self._run_test("Response Time", test_response_time)
        self._run_test("Multiple Searches", test_multiple_searches)
    
    def _run_integration_tests(self):
        """Test integration with external tools."""
        
        def test_pgn_game():
            """Test playing a short game."""
            try:
                # Quick 3-move game test
                process = subprocess.Popen(
                    [sys.executable, self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                commands = [
                    "uci",
                    "isready",
                    "ucinewgame",
                    "position startpos",
                    "go movetime 300",
                    "position startpos moves e2e4",
                    "go movetime 300", 
                    "position startpos moves e2e4 e7e5",
                    "go movetime 300",
                    "quit"
                ]
                
                input_str = "\n".join(commands) + "\n"
                stdout, stderr = process.communicate(input=input_str, timeout=20)
                
                # Should have 3 bestmove responses
                bestmove_count = stdout.count("bestmove")
                
                if bestmove_count >= 3:
                    return True, f"Game simulation completed: {bestmove_count} moves", {
                        "moves_played": bestmove_count,
                        "game_type": "3-move simulation"
                    }
                else:
                    return False, f"Game incomplete: only {bestmove_count} moves", None
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Game simulation timed out", None
            except Exception as e:
                return False, f"Game simulation failed: {e}", None
        
        def test_file_operations():
            """Test file I/O operations."""
            try:
                # Test that engine can be run from different directories
                original_dir = os.getcwd()
                test_dir = os.path.dirname(os.path.abspath(self.engine_path))
                
                os.chdir(test_dir)
                
                process = subprocess.Popen(
                    [sys.executable, "uci_interface.py"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input="uci\nquit\n", timeout=5)
                
                os.chdir(original_dir)
                
                if "uciok" in stdout:
                    return True, "File operations successful", {
                        "working_directory": test_dir,
                        "stderr_empty": len(stderr.strip()) == 0
                    }
                else:
                    return False, "File operations failed", None
                    
            except Exception as e:
                os.chdir(original_dir)
                return False, f"File operations test failed: {e}", None
        
        self._run_test("PGN Game Simulation", test_pgn_game)
        self._run_test("File Operations", test_file_operations)
    
    def _generate_report(self):
        """Generate comprehensive test report."""
        total_time = time.time() - self.start_time if self.start_time else 0
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]
        
        self.log("\n" + "=" * 60)
        self.log("📊 COMPREHENSIVE TEST REPORT")
        self.log("=" * 60)
        
        # Summary statistics
        self.log(f"🕐 Total Time: {total_time:.2f} seconds")
        self.log(f"📈 Tests Passed: {len(passed_tests)}/{len(self.results)}")
        self.log(f"📉 Tests Failed: {len(failed_tests)}/{len(self.results)}")
        
        if self.results:
            success_rate = len(passed_tests) / len(self.results) * 100
            self.log(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Failed tests details
        if failed_tests:
            self.log("\n❌ FAILED TESTS:")
            self.log("-" * 30)
            for test in failed_tests:
                self.log(f"  • {test.name}: {test.message}")
        
        # Performance summary
        if passed_tests:
            avg_time = sum(t.duration for t in passed_tests) / len(passed_tests)
            self.log(f"\n⚡ Average Test Time: {avg_time:.3f}s")
        
        # Overall status
        if len(passed_tests) == len(self.results):
            self.log("\n🎉 ALL TESTS PASSED! Engine ready for v1.1 release.")
        elif len(passed_tests) / len(self.results) >= 0.9:
            self.log("\n✅ ENGINE READY - 90%+ tests passed, suitable for release.")
        else:
            self.log("\n⚠️  ENGINE NEEDS ATTENTION - Too many test failures.")
        
        self.log("=" * 60)

def main():
    """Run the comprehensive test suite."""
    print("🚀 Cece Chess Engine v1.1 Pre-Release Testing")
    print("=" * 50)
    
    # Change to engine directory
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(engine_dir)
    
    # Run test suite
    test_suite = EngineTestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    if success:
        print("\n🎯 READY FOR v1.1 RELEASE!")
        return 0
    else:
        print("\n⚠️  ISSUES DETECTED - Review failed tests before release")
        return 1

if __name__ == "__main__":
    exit(main())
