"""
UCI (Universal Chess Interface) implementation for the chess engine.
"""

import sys
import threading
from engine import ChessEngine
from bitboard import Move, Square


class UCIInterface:
    """UCI protocol handler."""
    
    def __init__(self):
        self.engine = ChessEngine()
        self.search_thread = None
        self.stop_search = False
        
    def run(self):
        """Main UCI loop."""
        while True:
            try:
                command = input().strip()
                self.handle_command(command)
            except EOFError:
                break
            except KeyboardInterrupt:
                break
    
    def handle_command(self, command: str):
        """Handle UCI commands."""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        if cmd == "uci":
            self.handle_uci()
        elif cmd == "isready":
            self.handle_isready()
        elif cmd == "ucinewgame":
            self.handle_ucinewgame()
        elif cmd == "position":
            self.handle_position(parts[1:])
        elif cmd == "go":
            self.handle_go(parts[1:])
        elif cmd == "stop":
            self.handle_stop()
        elif cmd == "quit":
            self.handle_quit()
        elif cmd == "d" or cmd == "display":
            # Non-standard command for debugging
            self.engine.print_board()
        else:
            pass  # Unknown command, ignore
    
    def handle_uci(self):
        """Handle 'uci' command."""
        print("id name Static Evaluation Engine")
        print("id author Python Chess Engine")
        print("option name Hash type spin default 32 min 1 max 1024")
        print("option name Threads type spin default 1 min 1 max 8")
        print("uciok")
    
    def handle_isready(self):
        """Handle 'isready' command."""
        print("readyok")
    
    def handle_ucinewgame(self):
        """Handle 'ucinewgame' command."""
        self.engine = ChessEngine()
    
    def handle_position(self, args):
        """Handle 'position' command."""
        if not args:
            return
        
        if args[0] == "startpos":
            self.engine.set_position()
            move_idx = 2 if len(args) > 1 and args[1] == "moves" else 1
        elif args[0] == "fen":
            # Find where moves start
            move_idx = None
            fen_parts = []
            
            for i, arg in enumerate(args[1:], 1):
                if arg == "moves":
                    move_idx = i + 1
                    break
                fen_parts.append(arg)
            
            if fen_parts:
                fen = " ".join(fen_parts)
                self.engine.set_position(fen)
        else:
            return
        
        # Apply moves
        if move_idx and move_idx < len(args):
            for move_str in args[move_idx:]:
                if not self.engine.make_move_string(move_str):
                    print(f"info string Invalid move: {move_str}")
                    break
    
    def handle_go(self, args):
        """Handle 'go' command."""
        # Parse go parameters
        depth = None
        movetime = None
        wtime = None
        btime = None
        winc = None
        binc = None
        
        i = 0
        while i < len(args):
            if args[i] == "depth" and i + 1 < len(args):
                depth = int(args[i + 1])
                i += 2
            elif args[i] == "movetime" and i + 1 < len(args):
                movetime = int(args[i + 1]) / 1000.0  # Convert ms to seconds
                i += 2
            elif args[i] == "wtime" and i + 1 < len(args):
                wtime = int(args[i + 1]) / 1000.0
                i += 2
            elif args[i] == "btime" and i + 1 < len(args):
                btime = int(args[i + 1]) / 1000.0
                i += 2
            elif args[i] == "winc" and i + 1 < len(args):
                winc = int(args[i + 1]) / 1000.0
                i += 2
            elif args[i] == "binc" and i + 1 < len(args):
                binc = int(args[i + 1]) / 1000.0
                i += 2
            else:
                i += 1
        
        # Determine search parameters
        search_depth = depth if depth else 6
        search_time = movetime if movetime else 5.0
        
        # Time management (simplified)
        if not movetime and (wtime or btime):
            from bitboard import Color
            my_time = wtime if self.engine.board.to_move == Color.WHITE else btime
            if my_time:
                # Use a fraction of remaining time
                search_time = min(my_time / 30, 10.0)
        
        # Start search in separate thread
        self.stop_search = False
        self.search_thread = threading.Thread(
            target=self.search_worker, 
            args=(search_depth, search_time)
        )
        self.search_thread.start()
    
    def search_worker(self, depth: int, time_limit: float):
        """Worker function for search."""
        try:
            best_move = self.engine.get_best_move(depth, time_limit)
            if best_move and not self.stop_search:
                print(f"bestmove {best_move}")
            else:
                # No legal moves or search stopped
                legal_moves = self.engine.get_legal_moves()
                if legal_moves:
                    print(f"bestmove {legal_moves[0]}")
                else:
                    print("bestmove 0000")  # No legal moves
        except Exception as e:
            print(f"info string Error in search: {e}")
            print("bestmove 0000")
    
    def handle_stop(self):
        """Handle 'stop' command."""
        self.stop_search = True
        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join(timeout=1.0)
    
    def handle_quit(self):
        """Handle 'quit' command."""
        self.handle_stop()
        sys.exit(0)


def main():
    """Main entry point for UCI interface."""
    uci = UCIInterface()
    uci.run()


if __name__ == "__main__":
    main()