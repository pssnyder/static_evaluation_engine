"""
UCI (Universal Chess Interface) Implementation for Hybrid Engine

This provides a standard interface for chess GUIs and other engines to communicate
with your hybrid engine. The UCI protocol is the standard way chess engines
communicate with chess software.

Author: Your Name
License: GPL-3.0 (compatible with python-chess)
Attribution: Built on python-chess library by Niklas Fiekas
"""

import sys
import threading
from typing import Optional, List
from engine import ChessEngine
import chess


class UCIInterface:
    """
    UCI protocol implementation for the hybrid chess engine.
    
    This allows your engine to work with:
    - Chess GUIs (ChessBase, Arena, etc.)
    - Online platforms
    - Engine tournaments
    - Analysis tools
    """
    
    def __init__(self):
        self.engine = ChessEngine()
        self.running = True
        self.debug = False
        
    def send(self, message: str):
        """Send a message to the GUI."""
        print(message, flush=True)
        if self.debug:
            print(f">>> {message}", file=sys.stderr, flush=True)
    
    def log(self, message: str):
        """Log debug information."""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr, flush=True)
    
    def handle_uci(self):
        """Handle the 'uci' command - identify the engine."""
        self.send(f"id name {self.engine.info['name']}")
        self.send(f"id author {self.engine.info['author']}")
        
        # Engine options that can be configured
        self.send("option name Debug type check default false")
        self.send("option name Hash type spin default 64 min 1 max 1024")
        self.send("option name Threads type spin default 1 min 1 max 8")
        self.send("option name MaterialWeight type spin default 100 min 50 max 200")
        self.send("option name PositionalWeight type spin default 30 min 0 max 100")
        self.send("option name TacticalWeight type spin default 20 min 0 max 100")
        self.send("option name SafetyWeight type spin default 15 min 0 max 100")
        
        self.send("uciok")
    
    def handle_isready(self):
        """Handle the 'isready' command."""
        self.send("readyok")
    
    def handle_setoption(self, parts: List[str]):
        """Handle the 'setoption' command."""
        if len(parts) >= 4 and parts[1] == "name":
            name = parts[2]
            if len(parts) >= 5 and parts[3] == "value":
                value = parts[4]
                
                if name == "Debug":
                    self.debug = value.lower() == "true"
                    self.log(f"Debug mode: {self.debug}")
                elif name == "Hash":
                    # Note: python-chess doesn't use hash tables in the same way
                    # but we acknowledge the setting
                    self.log(f"Hash size set to {value} MB")
                elif name == "Threads":
                    self.log(f"Threads set to {value}")
                elif name == "MaterialWeight":
                    weight = float(value) / 100.0
                    self.engine.tune_evaluation("material", weight)
                    self.log(f"Material weight set to {weight}")
                elif name == "PositionalWeight":
                    weight = float(value) / 100.0
                    self.engine.tune_evaluation("positional", weight)
                    self.log(f"Positional weight set to {weight}")
                elif name == "TacticalWeight":
                    weight = float(value) / 100.0
                    self.engine.tune_evaluation("tactical", weight)
                    self.log(f"Tactical weight set to {weight}")
                elif name == "SafetyWeight":
                    weight = float(value) / 100.0
                    self.engine.tune_evaluation("safety", weight)
                    self.log(f"Safety weight set to {weight}")
    
    def handle_ucinewgame(self):
        """Handle the 'ucinewgame' command."""
        # Reset the engine for a new game
        self.engine = ChessEngine()
        self.log("New game started")
    
    def handle_position(self, parts: List[str]):
        """Handle the 'position' command."""
        if len(parts) < 2:
            return
        
        if parts[1] == "startpos":
            # Starting position
            fen = None
            moves_start = 2
            if len(parts) > 2 and parts[2] == "moves":
                moves_start = 3
        elif parts[1] == "fen":
            # FEN position
            if len(parts) < 8:
                return
            fen = " ".join(parts[2:8])
            moves_start = 8
            if len(parts) > 8 and parts[8] == "moves":
                moves_start = 9
        else:
            return
        
        # Extract moves if present
        moves = []
        if moves_start < len(parts):
            moves = parts[moves_start:]
        
        # Set position on engine
        self.engine.set_position(fen, moves)
        self.log(f"Position set: {self.engine.engine.board.fen()}")
    
    def handle_go(self, parts: List[str]):
        """Handle the 'go' command - start searching."""
        # Parse go command parameters
        depth = None
        movetime = None
        wtime = None
        btime = None
        winc = None
        binc = None
        infinite = False
        
        i = 1
        while i < len(parts):
            if parts[i] == "depth":
                if i + 1 < len(parts):
                    depth = int(parts[i + 1])
                    i += 2
                else:
                    i += 1
            elif parts[i] == "movetime":
                if i + 1 < len(parts):
                    movetime = float(parts[i + 1]) / 1000.0  # Convert ms to seconds
                    i += 2
                else:
                    i += 1
            elif parts[i] == "wtime":
                if i + 1 < len(parts):
                    wtime = int(parts[i + 1])
                    i += 2
                else:
                    i += 1
            elif parts[i] == "btime":
                if i + 1 < len(parts):
                    btime = int(parts[i + 1])
                    i += 2
                else:
                    i += 1
            elif parts[i] == "winc":
                if i + 1 < len(parts):
                    winc = int(parts[i + 1])
                    i += 2
                else:
                    i += 1
            elif parts[i] == "binc":
                if i + 1 < len(parts):
                    binc = int(parts[i + 1])
                    i += 2
                else:
                    i += 1
            elif parts[i] == "infinite":
                infinite = True
                i += 1
            else:
                i += 1
        
        # Determine search parameters
        search_depth = depth if depth is not None else self.engine.search_depth
        time_limit = movetime if movetime is not None else self.engine.time_limit
        
        # If we have time controls, calculate time for this move
        if wtime is not None and btime is not None:
            # Simple time management: use 1/30th of remaining time
            side_time = wtime if self.engine.engine.board.turn == chess.WHITE else btime
            time_limit = min(side_time / 30000.0, 10.0)  # Convert ms to seconds, max 10s
        
        self.log(f"Searching: depth={search_depth}, time={time_limit}s")
        
        # Start search in a separate thread to allow for stop commands
        search_thread = threading.Thread(
            target=self._search_and_respond,
            args=(search_depth, time_limit)
        )
        search_thread.start()
    
    def _search_and_respond(self, depth: int, time_limit: float):
        """Perform the search and send the result."""
        try:
            best_move = self.engine.get_best_move(depth, time_limit)
            if best_move:
                self.send(f"bestmove {best_move}")
            else:
                # No legal moves (checkmate or stalemate)
                self.send("bestmove 0000")
        except Exception as e:
            self.log(f"Search error: {e}")
            self.send("bestmove 0000")
    
    def handle_stop(self):
        """Handle the 'stop' command."""
        # For now, we don't implement search interruption
        # The search will complete and return normally
        self.log("Stop command received")
    
    def handle_quit(self):
        """Handle the 'quit' command."""
        self.running = False
        self.log("Quitting...")
    
    def run(self):
        """Main UCI loop."""
        self.log(f"Starting {self.engine.info['name']} UCI interface")
        
        while self.running:
            try:
                line = input().strip()
                if not line:
                    continue
                
                self.log(f"<<< {line}")
                parts = line.split()
                
                if not parts:
                    continue
                
                command = parts[0]
                
                if command == "uci":
                    self.handle_uci()
                elif command == "isready":
                    self.handle_isready()
                elif command == "setoption":
                    self.handle_setoption(parts)
                elif command == "ucinewgame":
                    self.handle_ucinewgame()
                elif command == "position":
                    self.handle_position(parts)
                elif command == "go":
                    self.handle_go(parts)
                elif command == "stop":
                    self.handle_stop()
                elif command == "quit":
                    self.handle_quit()
                else:
                    self.log(f"Unknown command: {command}")
                    
            except EOFError:
                break
            except Exception as e:
                self.log(f"Error processing command: {e}")


def main():
    """Entry point for UCI interface."""
    uci = UCIInterface()
    uci.run()


if __name__ == "__main__":
    main()
