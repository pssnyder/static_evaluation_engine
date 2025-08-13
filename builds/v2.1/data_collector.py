"""
Data Collection System for Chess Engine Analysis

This module implements the "thoughts" and "ideas" data collection framework
for detailed analysis of chess engine decision-making processes.

Definitions:
- "Thought": Individual evaluation decision/calculation for a specific position
- "Idea": Complete principal variation with full evaluation context

Author: Your Name  
License: GPL-3.0
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Thought:
    """
    A single evaluation decision/calculation.
    
    Represents one "firing synapse" in the engine's thinking process,
    capturing all the detailed scoring information for a specific position.
    """
    position_fen: str
    timestamp: float
    material_score: int
    positional_score: int
    tactical_score: int
    safety_score: int
    pawn_structure: int
    piece_activity: int
    custom_patterns: Dict[str, Any]
    total_score: int
    depth: int = 0
    move_leading_here: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert thought to dictionary for export."""
        return asdict(self)


@dataclass 
class Idea:
    """
    A complete principal variation representing a fully-formed strategic concept.
    
    Ideas are composed of multiple thoughts and represent the engine's
    best understanding of how a position should be played.
    """
    id: str
    timestamp: float
    depth: int
    principal_variation: List[str]
    evaluation_score: int
    nodes_searched: int
    time_to_find: float
    position_fen: str
    constituent_thoughts: List[str]  # References to thought IDs
    confidence_level: float = 0.0
    tactical_themes: Optional[List[str]] = None
    strategic_assessment: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tactical_themes is None:
            self.tactical_themes = []
        if self.strategic_assessment is None:
            self.strategic_assessment = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert idea to dictionary for export."""
        return asdict(self)


class ThoughtCollector:
    """
    Collects and manages individual evaluation thoughts for analysis.
    
    This system captures every evaluation calculation the engine makes,
    providing granular insight into the decision-making process.
    """
    
    def __init__(self):
        self.thoughts: List[Thought] = []
        self.current_session_id = self._generate_session_id()
        self.stats = {
            'total_thoughts': 0,
            'session_start': time.time(),
            'positions_evaluated': set(),
            'depth_distribution': {},
            'scoring_patterns': {}
        }
    
    def add_thought(self, thought_data: Dict[str, Any]) -> str:
        """
        Add a new thought to the collection.
        
        Args:
            thought_data: Dictionary containing all evaluation components
            
        Returns:
            Unique thought ID for reference tracking
        """
        thought_id = f"thought_{self.current_session_id}_{len(self.thoughts)}"
        
        thought = Thought(
            position_fen=thought_data.get('position_fen', ''),
            timestamp=thought_data.get('timestamp', time.time()),
            material_score=thought_data.get('material_score', 0),
            positional_score=thought_data.get('positional_score', 0),
            tactical_score=thought_data.get('tactical_score', 0),
            safety_score=thought_data.get('safety_score', 0),
            pawn_structure=thought_data.get('pawn_structure', 0),
            piece_activity=thought_data.get('piece_activity', 0),
            custom_patterns=thought_data.get('custom_patterns', {}),
            total_score=thought_data.get('total_score', 0),
            depth=thought_data.get('depth', 0),
            move_leading_here=thought_data.get('move_leading_here')
        )
        
        self.thoughts.append(thought)
        self._update_stats(thought)
        
        return thought_id
    
    def get_thoughts_for_position(self, fen: str) -> List[Thought]:
        """Get all thoughts for a specific position."""
        return [t for t in self.thoughts if t.position_fen == fen]
    
    def get_thoughts_by_depth(self, depth: int) -> List[Thought]:
        """Get all thoughts from a specific search depth."""
        return [t for t in self.thoughts if t.depth == depth]
    
    def get_recent_thoughts(self, count: int = 10) -> List[Thought]:
        """Get the most recent thoughts."""
        return self.thoughts[-count:] if len(self.thoughts) >= count else self.thoughts
    
    def analyze_scoring_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in the scoring components.
        
        Returns insights about how different evaluation components
        are being weighted and used across positions.
        """
        if not self.thoughts:
            return {}
        
        analysis = {
            'component_averages': {},
            'component_ranges': {},
            'correlation_patterns': {},
            'dominant_factors': {}
        }
        
        # Calculate component statistics
        components = ['material_score', 'positional_score', 'tactical_score', 
                     'safety_score', 'pawn_structure', 'piece_activity']
        
        for component in components:
            values = [getattr(t, component) for t in self.thoughts]
            if values:
                analysis['component_averages'][component] = sum(values) / len(values)
                analysis['component_ranges'][component] = {
                    'min': min(values),
                    'max': max(values),
                    'span': max(values) - min(values)
                }
        
        return analysis
    
    def export_data(self, format_type: str = 'dict') -> List[Dict[str, Any]]:
        """
        Export thoughts data for analysis.
        
        Args:
            format_type: 'dict', 'json', or 'csv'
            
        Returns:
            List of thought data in requested format
        """
        if format_type == 'dict':
            return [t.to_dict() for t in self.thoughts]
        elif format_type == 'json':
            # Return the data as dicts, not JSON strings
            return [t.to_dict() for t in self.thoughts]
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def clear(self):
        """Clear all collected thoughts."""
        self.thoughts.clear()
        self.stats['positions_evaluated'].clear()
        self.stats['depth_distribution'].clear()
    
    def count(self) -> int:
        """Get total number of thoughts collected."""
        return len(self.thoughts)
    
    def _update_stats(self, thought: Thought):
        """Update collection statistics."""
        self.stats['total_thoughts'] += 1
        self.stats['positions_evaluated'].add(thought.position_fen)
        
        depth_key = str(thought.depth)
        self.stats['depth_distribution'][depth_key] = \
            self.stats['depth_distribution'].get(depth_key, 0) + 1
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")


class IdeaCollector:
    """
    Collects and manages complete strategic ideas (principal variations).
    
    Ideas represent the engine's fully-formed strategic concepts and
    preferred lines of play.
    """
    
    def __init__(self):
        self.ideas: List[Idea] = []
        self.current_session_id = self._generate_session_id()
        self.stats = {
            'total_ideas': 0,
            'session_start': time.time(),
            'depth_progression': [],
            'evaluation_trends': [],
            'pv_length_distribution': {}
        }
    
    def add_idea(self, idea_data: Dict[str, Any]) -> str:
        """
        Add a new idea to the collection.
        
        Args:
            idea_data: Dictionary containing PV and evaluation data
            
        Returns:
            Unique idea ID for reference tracking
        """
        idea_id = f"idea_{self.current_session_id}_{len(self.ideas)}"
        
        idea = Idea(
            id=idea_id,
            timestamp=idea_data.get('timestamp', time.time()),
            depth=idea_data.get('depth', 0),
            principal_variation=idea_data.get('principal_variation', []),
            evaluation_score=idea_data.get('evaluation_score', 0),
            nodes_searched=idea_data.get('nodes_searched', 0),
            time_to_find=idea_data.get('time_to_find', 0.0),
            position_fen=idea_data.get('position_fen', ''),
            constituent_thoughts=idea_data.get('constituent_thoughts', []),
            confidence_level=idea_data.get('confidence_level', 0.0),
            tactical_themes=idea_data.get('tactical_themes', []),
            strategic_assessment=idea_data.get('strategic_assessment', {})
        )
        
        self.ideas.append(idea)
        self._update_stats(idea)
        
        return idea_id
    
    def get_ideas_by_depth(self, depth: int) -> List[Idea]:
        """Get all ideas from a specific search depth."""
        return [i for i in self.ideas if i.depth == depth]
    
    def get_best_ideas(self, count: int = 5) -> List[Idea]:
        """Get the highest-scoring ideas."""
        return sorted(self.ideas, key=lambda i: abs(i.evaluation_score), reverse=True)[:count]
    
    def get_idea_evolution(self) -> List[Idea]:
        """
        Get ideas in chronological order to see how thinking evolved.
        
        This shows how the engine's preferred line changed during search.
        """
        return sorted(self.ideas, key=lambda i: i.timestamp)
    
    def analyze_convergence(self) -> Dict[str, Any]:
        """
        Analyze how ideas converged during search.
        
        Returns insights about search stability and confidence.
        """
        if len(self.ideas) < 2:
            return {}
        
        evolution = self.get_idea_evolution()
        
        analysis = {
            'score_stability': self._calculate_score_stability(evolution),
            'pv_stability': self._calculate_pv_stability(evolution),
            'convergence_rate': self._calculate_convergence_rate(evolution),
            'final_confidence': evolution[-1].confidence_level if evolution else 0.0
        }
        
        return analysis
    
    def export_data(self, format_type: str = 'dict') -> List[Dict[str, Any]]:
        """Export ideas data for analysis."""
        if format_type == 'dict':
            return [i.to_dict() for i in self.ideas]
        elif format_type == 'json':
            # Return the data as dicts, not JSON strings
            return [i.to_dict() for i in self.ideas]
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def clear(self):
        """Clear all collected ideas."""
        self.ideas.clear()
        self.stats['depth_progression'].clear()
        self.stats['evaluation_trends'].clear()
        self.stats['pv_length_distribution'].clear()
    
    def count(self) -> int:
        """Get total number of ideas collected."""
        return len(self.ideas)
    
    def _update_stats(self, idea: Idea):
        """Update collection statistics."""
        self.stats['total_ideas'] += 1
        self.stats['depth_progression'].append(idea.depth)
        self.stats['evaluation_trends'].append(idea.evaluation_score)
        
        pv_length = len(idea.principal_variation)
        pv_key = str(pv_length)
        self.stats['pv_length_distribution'][pv_key] = \
            self.stats['pv_length_distribution'].get(pv_key, 0) + 1
    
    def _calculate_score_stability(self, evolution: List[Idea]) -> float:
        """Calculate how stable evaluation scores were across search."""
        if len(evolution) < 2:
            return 1.0
        
        scores = [i.evaluation_score for i in evolution]
        total_variation = sum(abs(scores[i] - scores[i-1]) for i in range(1, len(scores)))
        avg_score = sum(abs(s) for s in scores) / len(scores)
        
        return 1.0 - min(1.0, total_variation / max(avg_score * len(scores), 1))
    
    def _calculate_pv_stability(self, evolution: List[Idea]) -> float:
        """Calculate how stable the principal variation was."""
        if len(evolution) < 2:
            return 1.0
        
        stability_sum = 0
        comparisons = 0
        
        for i in range(1, len(evolution)):
            prev_pv = evolution[i-1].principal_variation
            curr_pv = evolution[i].principal_variation
            
            if prev_pv and curr_pv:
                # Compare first few moves
                compare_length = min(len(prev_pv), len(curr_pv), 3)
                if compare_length > 0:
                    matches = sum(1 for j in range(compare_length) 
                                if prev_pv[j] == curr_pv[j])
                    stability_sum += matches / compare_length
                    comparisons += 1
        
        return stability_sum / max(comparisons, 1)
    
    def _calculate_convergence_rate(self, evolution: List[Idea]) -> float:
        """Calculate how quickly the search converged on the final idea."""
        if len(evolution) < 2:
            return 1.0
        
        final_pv = evolution[-1].principal_variation
        if not final_pv:
            return 0.0
        
        final_move = final_pv[0] if final_pv else None
        convergence_point = 0
        
        for i, idea in enumerate(evolution):
            if idea.principal_variation and idea.principal_variation[0] == final_move:
                convergence_point = i
                break
        
        return 1.0 - (convergence_point / max(len(evolution) - 1, 1))
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
