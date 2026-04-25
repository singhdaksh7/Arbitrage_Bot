"""
Latency metrics tracking: detection → execution end-to-end timing
"""

import time
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class LatencyPhase:
    """Individual phase timing"""
    name: str
    start: float = 0.0
    end: float = 0.0
    
    @property
    def duration_ms(self) -> float:
        if self.end == 0:
            return 0
        return (self.end - self.start) * 1000


class LatencyTracker:
    """
    Track execution latency across all phases:
    - Price Fetch: Time to get all exchange prices
    - Comparison: Time to identify opportunities
    - Preparation: Time to prepare orders
    - Submission: Time to submit orders to exchange
    - Confirmation: Time to receive fill confirmation
    """
    
    def __init__(self):
        self.phases: List[LatencyPhase] = []
        self.current_phase: Dict = {}
        self.total_samples = 0
        self.latency_stats = {
            'detection_to_execution_ms': [],
            'price_fetch_ms': [],
            'comparison_ms': [],
            'order_preparation_ms': [],
            'order_submission_ms': [],
            'order_confirmation_ms': []
        }
    
    def start_phase(self, phase_name: str):
        """Begin timing a phase"""
        self.current_phase[phase_name] = time.time()
    
    def end_phase(self, phase_name: str) -> float:
        """
        End timing a phase, return duration in ms.
        """
        if phase_name not in self.current_phase:
            return 0
        
        duration = (time.time() - self.current_phase[phase_name]) * 1000
        
        phase = LatencyPhase(name=phase_name, start=self.current_phase[phase_name], end=time.time())
        self.phases.append(phase)
        del self.current_phase[phase_name]
        
        # Store in appropriate bucket
        if phase_name in self.latency_stats:
            self.latency_stats[phase_name].append(duration)
            # Keep only last 100 samples per phase
            if len(self.latency_stats[phase_name]) > 100:
                self.latency_stats[phase_name].pop(0)
        
        return duration
    
    def record_full_cycle(self, duration_ms: float):
        """Record total detection-to-execution time"""
        self.latency_stats['detection_to_execution_ms'].append(duration_ms)
        if len(self.latency_stats['detection_to_execution_ms']) > 100:
            self.latency_stats['detection_to_execution_ms'].pop(0)
        self.total_samples += 1
    
    def get_phase_summary(self, phase_name: str) -> Dict:
        """Get statistics for a single phase"""
        if phase_name not in self.latency_stats or not self.latency_stats[phase_name]:
            return {'count': 0, 'avg_ms': 0, 'min_ms': 0, 'max_ms': 0, 'p99_ms': 0}
        
        samples = sorted(self.latency_stats[phase_name])
        n = len(samples)
        
        return {
            'count': n,
            'avg_ms': round(sum(samples) / n, 2),
            'min_ms': round(samples[0], 2),
            'max_ms': round(samples[-1], 2),
            'p99_ms': round(samples[int(n * 0.99)] if n > 1 else samples[0], 2),
            'median_ms': round(samples[n // 2], 2)
        }
    
    def get_all_stats(self) -> Dict:
        """Get comprehensive latency statistics"""
        phases = {}
        for phase_name in self.latency_stats.keys():
            if self.latency_stats[phase_name]:
                phases[phase_name] = self.get_phase_summary(phase_name)
        
        # Calculate end-to-end
        e2e = self.latency_stats['detection_to_execution_ms']
        e2e_stats = {
            'count': len(e2e),
            'avg_ms': round(sum(e2e) / len(e2e), 2) if e2e else 0,
            'min_ms': round(min(e2e), 2) if e2e else 0,
            'max_ms': round(max(e2e), 2) if e2e else 0,
            'p99_ms': round(sorted(e2e)[int(len(e2e) * 0.99)] if e2e and len(e2e) > 1 else (sorted(e2e)[0] if e2e else 0), 2),
            'median_ms': round(sorted(e2e)[len(e2e) // 2], 2) if e2e else 0
        }
        
        return {
            'total_cycles': self.total_samples,
            'end_to_end': e2e_stats,
            'phases': phases
        }
    
    def reset(self):
        """Clear all statistics"""
        self.phases.clear()
        self.current_phase.clear()
        self.total_samples = 0
        for key in self.latency_stats:
            self.latency_stats[key].clear()


# Global tracker instance
latency_tracker = LatencyTracker()
