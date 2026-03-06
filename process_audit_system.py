"""
Process Audit System for Sweat the Assets Mission
Maps running processes to strategic goals and identifies optimization opportunities
"""

import psutil
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import firebase_admin
from firebase_admin import firestore, credentials
from collections import defaultdict
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('process_audit.log')
    ]
)
logger = logging.getLogger(__name__)


class StrategicGoal(Enum):
    """Core strategic goals for the Evolution Ecosystem"""
    TRADING_REVENUE = "trading_revenue"
    DATA_ANALYSIS = "data_analysis"
    MARKET_RESEARCH = "market_research"
    INFRASTRUCTURE = "infrastructure"
    MONITORING = "monitoring"
    UNKNOWN = "unknown"
    OPTIMIZATION_TARGET = "optimization_target"


@dataclass
class ProcessRecord:
    """Data class for process information with strategic mapping"""
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    strategic_goal: StrategicGoal
    revenue_impact: float  # 0-100 scale
    optimization_priority: int  # 1-5 (1 = highest)
    tags: List[str]
    timestamp: datetime = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for Firebase storage"""
        data = asdict(self)
        data['strategic_goal'] = self.strategic_goal.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ProcessAuditSystem:
    """Main system for auditing and optimizing running processes"""
    
    def __init__(self, firebase_cred_path: Optional[str] = None):
        self.process_map: Dict[int, ProcessRecord] = {}
        self.goal_mapping: Dict[str, StrategicGoal] = self._load_goal_mapping()
        self.resource_thresholds = {
            'high_cpu': 70.0,  # CPU% threshold for optimization
            'high_memory': 1024,  # MB threshold for optimization
            'low_priority_cpu': 10.0,  # CPU% below which process is low priority
        }
        
        # Initialize Firebase if credentials available
        self.firestore_client = None
        if firebase_cred_path and os.path.exists(firebase_cred_path):
            try:
                cred = credentials.Certificate(firebase_cred_path)
                firebase_admin.initialize_app(cred)
                self.firestore_client = firestore.client()
                logger.info("Firebase Firestore initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
        else:
            logger.warning("Firebase credentials not found, running in local mode only")
    
    def _load_goal_mapping(self) -> Dict[str, StrategicGoal]:
        """Load mapping of process names to strategic goals"""
        return {
            # Trading and Analysis
            'python': StrategicGoal.TRADING_REVENUE,
            'node': StrategicGoal.TRADING_REVENUE,
            'jupyter': StrategicGoal.DATA_ANALYSIS,
            'ccxt': StrategicGoal.TRADING_REVENUE,
            'alpaca': StrategicGoal.TRADING_REVENUE,
            
            # Market Research
            'scrapy': StrategicGoal.MARKET_RESEARCH,
            'beautifulsoup': StrategicGoal.MARKET_RESEARCH,
            'selenium': StrategicGoal.MARKET_RESEARCH,
            
            # Infrastructure
            'docker': StrategicGoal.INFRASTRUCTURE,
            'nginx': StrategicGoal.INFRASTRUCTURE,
            'redis': StrategicGoal.INFRASTRUCTURE,
            'postgres': StrategicGoal.INFRASTRUCTURE,
            
            # Monitoring
            'prometheus': StrategicGoal.MONITORING,
            'grafana': StrategicGoal.MONITORING,
            
            # Optimization Targets
            'chrome': StrategicGoal.OPTIMIZATION_TARGET,
            'firefox': StrategicGoal.OPTIMIZATION_TARGET,
            'slack': StrategicGoal.OPTIMIZATION_TARGET,
            'discord': StrategicGoal.OPTIMIZATION_TARGET,
        }
    
    def _classify_process(self, process_name: str) -> Tuple[StrategicGoal, float, int]:
        """Classify a process and determine its priority"""
        process_lower = process_name.lower()
        
        # Check for exact matches first
        for key, goal in self.goal_mapping.items():
            if key in process_lower:
                if goal == StrategicGoal.TRADING_REVENUE:
                    return goal, 95.0, 1  # Highest revenue impact, highest priority
                elif goal == StrategicGoal.DATA_ANALYSIS:
                    return goal, 80.0, 2
                elif goal == StrategicGoal.OPTIMIZATION_TARGET:
                    return goal, 10.0, 5  # Low revenue impact, lowest priority
                else:
                    return goal,