"""
AI Intelligence Engine - Real Machine Learning Implementation
- Behavioral Learning AI
- Pattern Detection AI
- Predictive CTR Optimization
- Anomaly Detection AI
- Proxy Intelligence AI
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.logger import logger


class BehavioralLearningAI:
    """AI untuk belajar pola behavior manusia"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "ai/models/behavior_model.pkl"
        self.scaler_path = "ai/models/behavior_scaler.pkl"
        
        # Load existing model if available
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                logger.info("✅ Behavioral AI: Loaded pre-trained model")
        except Exception as e:
            logger.warning(f"⚠️ Behavioral AI: Could not load model - {e}")
    
    def _save_model(self):
        """Save trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            logger.info("✅ Behavioral AI: Model saved successfully")
        except Exception as e:
            logger.error(f"❌ Behavioral AI: Failed to save model - {e}")
    
    def train(self, history_data: List[Dict]) -> bool:
        """
        Train model dari historical data
        
        Args:
            history_data: List of dicts dengan keys: scroll_count, delay, ctr, success
        
        Returns:
            True jika training berhasil
        """
        try:
            if len(history_data) < 20:
                logger.warning("⚠️ Behavioral AI: Not enough data to train (need min 20 samples)")
                return False
            
            # Prepare data
            df = pd.DataFrame(history_data)
            
            # Features: scroll_count, delay
            X = df[['scroll_count', 'delay']].values
            
            # Target: success rate
            y = df['success'].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Save model
            self._save_model()
            
            logger.info(f"✅ Behavioral AI: Trained on {len(history_data)} samples")
            return True
            
        except Exception as e:
            logger.error(f"❌ Behavioral AI: Training failed - {e}")
            return False
    
    def predict_optimal_behavior(self) -> Dict[str, float]:
        """
        Prediksi behavior optimal (scroll & delay) untuk success rate tertinggi
        
        Returns:
            Dict dengan keys: scroll_count, delay
        """
        try:
            if not self.is_trained:
                # Return default jika belum trained
                return {
                    'scroll_count': 45,
                    'delay': 25
                }
            
            # Test berbagai kombinasi
            best_scroll = 45
            best_delay = 25
            best_score = 0
            
            for scroll in range(30, 61, 5):
                for delay in range(20, 31, 2):
                    X = np.array([[scroll, delay]])
                    X_scaled = self.scaler.transform(X)
                    score = self.model.predict(X_scaled)[0]
                    
                    if score > best_score:
                        best_score = score
                        best_scroll = scroll
                        best_delay = delay
            
            logger.info(f"🧠 Behavioral AI: Optimal behavior → scroll={best_scroll}, delay={best_delay}s (score={best_score:.2f})")
            
            return {
                'scroll_count': best_scroll,
                'delay': best_delay
            }
            
        except Exception as e:
            logger.error(f"❌ Behavioral AI: Prediction failed - {e}")
            return {'scroll_count': 45, 'delay': 25}


class PatternDetectionAI:
    """AI untuk deteksi pola CAPTCHA dan blocking"""
    
    def __init__(self):
        self.captcha_patterns = []
        self.block_patterns = []
        self.pattern_file = "ai/models/patterns.json"
        
        # Load existing patterns
        self._load_patterns()
    
    def _load_patterns(self):
        """Load saved patterns"""
        try:
            if os.path.exists(self.pattern_file):
                with open(self.pattern_file, 'r') as f:
                    data = json.load(f)
                    self.captcha_patterns = data.get('captcha', [])
                    self.block_patterns = data.get('blocks', [])
                logger.info(f"✅ Pattern AI: Loaded {len(self.captcha_patterns)} captcha patterns")
        except Exception as e:
            logger.warning(f"⚠️ Pattern AI: Could not load patterns - {e}")
    
    def _save_patterns(self):
        """Save patterns"""
        try:
            os.makedirs(os.path.dirname(self.pattern_file), exist_ok=True)
            with open(self.pattern_file, 'w') as f:
                json.dump({
                    'captcha': self.captcha_patterns,
                    'blocks': self.block_patterns
                }, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Pattern AI: Failed to save patterns - {e}")
    
    def learn_captcha_pattern(self, url: str, page_title: str, page_source: str):
        """Learn new captcha pattern"""
        try:
            pattern = {
                'url': url.lower(),
                'title': page_title.lower(),
                'keywords': self._extract_keywords(page_source),
                'timestamp': datetime.now().isoformat()
            }
            
            # Avoid duplicates
            if not any(p['url'] == pattern['url'] for p in self.captcha_patterns):
                self.captcha_patterns.append(pattern)
                self._save_patterns()
                logger.info(f"🧠 Pattern AI: Learned new CAPTCHA pattern from {url[:50]}")
        
        except Exception as e:
            logger.error(f"❌ Pattern AI: Failed to learn pattern - {e}")
    
    def _extract_keywords(self, page_source: str) -> List[str]:
        """Extract important keywords dari page source"""
        keywords = []
        source_lower = page_source.lower()
        
        important_words = [
            'captcha', 'recaptcha', 'hcaptcha', 'verify', 'challenge',
            'cloudflare', 'protection', 'security', 'robot', 'human'
        ]
        
        for word in important_words:
            if word in source_lower:
                keywords.append(word)
        
        return keywords
    
    def is_captcha_likely(self, url: str, title: str) -> bool:
        """Check apakah URL/title match dengan known patterns"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        for pattern in self.captcha_patterns:
            if pattern['url'] in url_lower or any(kw in title_lower for kw in pattern.get('keywords', [])):
                return True
        
        return False


class PredictiveCTROptimization:
    """AI untuk prediksi CTR optimal"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "ai/models/ctr_model.pkl"
        self.scaler_path = "ai/models/ctr_scaler.pkl"
        
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                logger.info("✅ CTR AI: Loaded pre-trained model")
        except Exception as e:
            logger.warning(f"⚠️ CTR AI: Could not load model - {e}")
    
    def _save_model(self):
        """Save model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            logger.info("✅ CTR AI: Model saved")
        except Exception as e:
            logger.error(f"❌ CTR AI: Failed to save - {e}")
    
    def train(self, history_data: List[Dict]) -> bool:
        """Train CTR optimization model"""
        try:
            if len(history_data) < 15:
                return False
            
            df = pd.DataFrame(history_data)
            
            # Features: target_ctr, actual_clicks, total_visits
            X = df[['target_ctr', 'scroll_count', 'delay']].values
            y = df['actual_ctr'].values
            
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            self._save_model()
            logger.info(f"✅ CTR AI: Trained on {len(history_data)} samples")
            return True
            
        except Exception as e:
            logger.error(f"❌ CTR AI: Training failed - {e}")
            return False
    
    def predict_optimal_ctr(self, scroll_count: int, delay: int) -> float:
        """Predict optimal CTR based on behavior"""
        try:
            if not self.is_trained:
                return 8.0  # Default
            
            # Try different CTR values
            best_ctr = 8.0
            best_score = 0
            
            for ctr in np.arange(5.0, 12.0, 0.5):
                X = np.array([[ctr, scroll_count, delay]])
                X_scaled = self.scaler.transform(X)
                score = self.model.predict(X_scaled)[0]
                
                if score > best_score:
                    best_score = score
                    best_ctr = ctr
            
            logger.info(f"🧠 CTR AI: Optimal CTR = {best_ctr:.1f}%")
            return best_ctr
            
        except Exception as e:
            logger.error(f"❌ CTR AI: Prediction failed - {e}")
            return 8.0


class AnomalyDetectionAI:
    """AI untuk deteksi anomali pada proxy/behavior"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, normal_data: List[Dict]) -> bool:
        """Train anomaly detector dengan normal behavior data"""
        try:
            if len(normal_data) < 30:
                return False
            
            df = pd.DataFrame(normal_data)
            X = df[['latency', 'success_rate', 'response_time']].values
            
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
            
            logger.info(f"✅ Anomaly AI: Trained on {len(normal_data)} samples")
            return True
            
        except Exception as e:
            logger.error(f"❌ Anomaly AI: Training failed - {e}")
            return False
    
    def is_anomaly(self, latency: float, success_rate: float, response_time: float) -> bool:
        """Detect if current behavior is anomaly"""
        try:
            if not self.is_trained:
                # Simple heuristic if not trained
                return latency > 10000 or success_rate < 0.3 or response_time > 30
            
            X = np.array([[latency, success_rate, response_time]])
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)[0]
            
            # -1 = anomaly, 1 = normal
            is_anomaly = (prediction == -1)
            
            if is_anomaly:
                logger.warning(f"⚠️ Anomaly AI: Detected unusual behavior!")
            
            return is_anomaly
            
        except Exception as e:
            logger.error(f"❌ Anomaly AI: Detection failed - {e}")
            return False


class ProxyIntelligenceAI:
    """AI untuk smart proxy selection"""
    
    def __init__(self):
        self.proxy_scores = {}  # {proxy: score}
        self.proxy_history = {}  # {proxy: [success, fail, latency]}
        self.score_file = "ai/models/proxy_scores.json"
        
        self._load_scores()
    
    def _load_scores(self):
        """Load proxy scores"""
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r') as f:
                    data = json.load(f)
                    self.proxy_scores = data.get('scores', {})
                    self.proxy_history = data.get('history', {})
                logger.info(f"✅ Proxy AI: Loaded {len(self.proxy_scores)} proxy scores")
        except Exception as e:
            logger.warning(f"⚠️ Proxy AI: Could not load scores - {e}")
    
    def _save_scores(self):
        """Save proxy scores"""
        try:
            os.makedirs(os.path.dirname(self.score_file), exist_ok=True)
            with open(self.score_file, 'w') as f:
                json.dump({
                    'scores': self.proxy_scores,
                    'history': self.proxy_history
                }, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Proxy AI: Failed to save scores - {e}")
    
    def update_proxy_performance(self, proxy: str, success: bool, latency: float):
        """Update proxy performance based on result"""
        try:
            if proxy not in self.proxy_history:
                self.proxy_history[proxy] = {'success': 0, 'fail': 0, 'latencies': []}
            
            if success:
                self.proxy_history[proxy]['success'] += 1
            else:
                self.proxy_history[proxy]['fail'] += 1
            
            self.proxy_history[proxy]['latencies'].append(latency)
            
            # Keep only last 20 latencies
            if len(self.proxy_history[proxy]['latencies']) > 20:
                self.proxy_history[proxy]['latencies'] = self.proxy_history[proxy]['latencies'][-20:]
            
            # Calculate score
            total = self.proxy_history[proxy]['success'] + self.proxy_history[proxy]['fail']
            success_rate = self.proxy_history[proxy]['success'] / total if total > 0 else 0.5
            avg_latency = np.mean(self.proxy_history[proxy]['latencies']) if self.proxy_history[proxy]['latencies'] else 5000
            
            # Score formula: success_rate * (1 - normalized_latency)
            normalized_latency = min(avg_latency / 10000, 1.0)
            score = success_rate * (1 - normalized_latency)
            
            self.proxy_scores[proxy] = score
            
            self._save_scores()
            
        except Exception as e:
            logger.error(f"❌ Proxy AI: Failed to update performance - {e}")
    
    def get_best_proxy(self, available_proxies: List[str]) -> str:
        """Get best proxy based on AI scoring"""
        try:
            if not available_proxies:
                return None
            
            # Score available proxies
            scored_proxies = []
            for proxy in available_proxies:
                score = self.proxy_scores.get(proxy, 0.5)  # Default score 0.5 for unknown
                scored_proxies.append((proxy, score))
            
            # Sort by score descending
            scored_proxies.sort(key=lambda x: x[1], reverse=True)
            
            # Use weighted random selection (favor high scores but add randomness)
            weights = [score for _, score in scored_proxies]
            total_weight = sum(weights)
            
            if total_weight == 0:
                return np.random.choice(available_proxies)
            
            probabilities = [w / total_weight for w in weights]
            selected = np.random.choice([p for p, _ in scored_proxies], p=probabilities)
            
            logger.info(f"🧠 Proxy AI: Selected {selected} (score={self.proxy_scores.get(selected, 0.5):.2f})")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Proxy AI: Selection failed - {e}")
            return np.random.choice(available_proxies) if available_proxies else None


class AIEngine:
    """Main AI Engine - Coordinator for all AI modules"""
    
    def __init__(self):
        """Initialize all AI modules"""
        logger.info("🤖 Initializing AI/ML Intelligence Engine...")
        
        self.behavioral_ai = BehavioralLearningAI()
        self.pattern_ai = PatternDetectionAI()
        self.ctr_ai = PredictiveCTROptimization()
        self.anomaly_ai = AnomalyDetectionAI()
        self.proxy_ai = ProxyIntelligenceAI()
        
        self.enabled = True
        
        logger.info("✅ AI Engine: All modules initialized successfully!")
    
    def train_from_history(self, history_db) -> bool:
        """Train all AI models from historical data"""
        try:
            from data.history import history_manager
            
            # Get historical data
            records = history_manager.get_all_records(limit=1000)
            
            if len(records) < 20:
                logger.warning("⚠️ AI Engine: Not enough historical data for training")
                return False
            
            # Prepare data for behavioral AI
            behavior_data = []
            ctr_data = []
            
            for record in records:
                behavior_data.append({
                    'scroll_count': record.get('scroll_count', 45),
                    'delay': record.get('delay', 25),
                    'success': 1 if record.get('status') == 'success' else 0
                })
                
                if 'ctr' in record:
                    ctr_data.append({
                        'target_ctr': record.get('target_ctr', 8.0),
                        'scroll_count': record.get('scroll_count', 45),
                        'delay': record.get('delay', 25),
                        'actual_ctr': record.get('ctr', 8.0)
                    })
            
            # Train models
            logger.info("🧠 AI Engine: Starting training process...")
            
            success_count = 0
            if self.behavioral_ai.train(behavior_data):
                success_count += 1
            
            if len(ctr_data) >= 15 and self.ctr_ai.train(ctr_data):
                success_count += 1
            
            logger.info(f"✅ AI Engine: Training complete! ({success_count}/2 models trained)")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ AI Engine: Training failed - {e}")
            return False
    
    def get_optimal_behavior(self) -> Dict:
        """Get AI-predicted optimal behavior"""
        return self.behavioral_ai.predict_optimal_behavior()
    
    def get_optimal_ctr(self, scroll_count: int, delay: int) -> float:
        """Get AI-predicted optimal CTR"""
        return self.ctr_ai.predict_optimal_ctr(scroll_count, delay)
    
    def select_best_proxy(self, available_proxies: List[str]) -> str:
        """AI-based proxy selection"""
        return self.proxy_ai.get_best_proxy(available_proxies)
    
    def update_proxy_performance(self, proxy: str, success: bool, latency: float):
        """Update proxy performance for learning"""
        self.proxy_ai.update_proxy_performance(proxy, success, latency)
    
    def learn_captcha_pattern(self, url: str, title: str, page_source: str):
        """Learn new captcha pattern"""
        self.pattern_ai.learn_captcha_pattern(url, title, page_source)
    
    def is_likely_captcha(self, url: str, title: str) -> bool:
        """Check if URL/title matches known captcha patterns"""
        return self.pattern_ai.is_captcha_likely(url, title)


# Global AI Engine instance
ai_engine = AIEngine()
