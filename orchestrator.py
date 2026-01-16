"""
Bot Orchestrator - Central Coordinator
Mengkoordinasi semua worker dan resource
"""

import threading
import time
from queue import Queue
from typing import List, Callable
from bot_config import config
from core.worker import BotWorker
from core.resource_manager import resource_manager
from utils.logger import logger
from utils.helpers import read_file_lines

class BotOrchestrator:
    """Central coordinator untuk semua bot operations"""
    
    def __init__(self):
        """Initialize orchestrator"""
        self.workers = {}
        self.active_threads = {}
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Task queue
        self.task_queue = Queue()
        
        # URLs and proxies
        self.urls = []
        self.proxies = []
        
        # Callbacks untuk UI updates
        self.status_callback = None
        self.worker_callback = None
        
        # Statistics
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
    
    def set_status_callback(self, callback: Callable):
        """Set callback untuk status updates di GUI"""
        self.status_callback = callback
    
    def set_worker_callback(self, callback: Callable):
        """Set callback untuk worker updates di GUI"""
        self.worker_callback = callback
    
    def load_resources(self) -> bool:
        """
        Load URLs dan proxies dari file
        
        Returns:
            True jika sukses
        """
        try:
            # Load URLs
            if not config.FILE_ARTICLES:
                logger.error("Article file not set!")
                if self.status_callback:
                    self.status_callback("[ERROR] Article file not configured!")
                return False
            
            self.urls = read_file_lines(config.FILE_ARTICLES)
            if not self.urls:
                logger.error("No URLs found in article file!")
                if self.status_callback:
                    self.status_callback("[ERROR] No URLs found in article file!")
                return False
            
            logger.info(f"Loaded {len(self.urls)} URLs")
            if self.status_callback:
                self.status_callback(f"[INFO] Loaded {len(self.urls)} URLs from article file")
            
            # Load proxies (optional)
            if config.FILE_PROXIES:
                self.proxies = read_file_lines(config.FILE_PROXIES)
                logger.info(f"Loaded {len(self.proxies)} proxies")
                if self.status_callback:
                    self.status_callback(f"[INFO] Loaded {len(self.proxies)} proxies")
            else:
                logger.warning("No proxy file set - running without proxy")
                if self.status_callback:
                    self.status_callback("[WARNING] Running WITHOUT proxy")
                self.proxies = []
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load resources: {e}")
            if self.status_callback:
                self.status_callback(f"[ERROR] Failed to load resources: {e}")
            return False
    
    def start(self, num_workers: int = None):
        """
        Start bot orchestrator
        
        Args:
            num_workers: Jumlah worker (default dari config)
        """
        if self.is_running:
            logger.warning("Bot already running!")
            if self.status_callback:
                self.status_callback("[WARNING] Bot already running!")
            return
        
        # Load resources
        if not self.load_resources():
            return
        
        # Determine worker count
        if num_workers is None:
            num_workers = min(config.TASK_COUNT, getattr(config, 'MAX_WORKERS', 100))
        
        logger.info(f"Starting bot with {num_workers} workers...")
        if self.status_callback:
            self.status_callback(f"[START] Launching {num_workers} workers...")
        
        self.is_running = True
        self.stop_event.clear()
        
        # Start workers
        for worker_id in range(1, num_workers + 1):
            self._start_worker(worker_id)
        
        logger.info(f"Bot started with {num_workers} workers!")
        if self.status_callback:
            self.status_callback(f"[SUCCESS] {num_workers} workers started successfully!")
    
    def _start_worker(self, worker_id: int):
        """Start single worker thread"""
        def worker_thread():
            worker = BotWorker(worker_id)
            self.workers[worker_id] = worker
            
            # Update GUI - worker card status
            if self.worker_callback:
                self.worker_callback(worker_id, "INITIALIZING", "#3498db", "Starting up...")
            
            # Log to GUI
            if self.status_callback:
                self.status_callback(f"[WORKER #{worker_id}] Initialized")
            
            retry_count = 0
            max_retries = getattr(config, 'MAX_RETRIES', 3)
            
            while not self.stop_event.is_set() and retry_count < max_retries:
                try:
                    # Pick random URL
                    import random
                    url = random.choice(self.urls)
                    url_short = url[:60] + "..." if len(url) > 60 else url
                    
                    # Update GUI - worker card
                    if self.worker_callback:
                        self.worker_callback(worker_id, "RUNNING", "#3498db", f"Visiting: {url_short}")
                    
                    # Log to GUI
                    if self.status_callback:
                        self.status_callback(f"[WORKER #{worker_id}] Visiting: {url_short}")
                    
                    # Execute task
                    success = worker.execute_task(url, self.proxies)
                    
                    if success:
                        self.total_tasks_completed += 1
                        retry_count = 0  # Reset retry count on success
                        
                        # Update GUI - worker card
                        if self.worker_callback:
                            self.worker_callback(worker_id, "SUCCESS", "#00b894", "Task completed!")
                        
                        # Log to GUI
                        if self.status_callback:
                            self.status_callback(f"[WORKER #{worker_id}] ✓ SUCCESS - Task completed!")
                        
                        # Delay before next task
                        if not self.stop_event.wait(getattr(config, 'RETRY_DELAY', 5)):
                            continue
                    else:
                        self.total_tasks_failed += 1
                        retry_count += 1
                        
                        # Update GUI - worker card
                        if self.worker_callback:
                            self.worker_callback(worker_id, "FAILED", "#e74c3c", f"Failed (retry {retry_count}/{max_retries})")
                        
                        # Log to GUI
                        if self.status_callback:
                            self.status_callback(f"[WORKER #{worker_id}] ✗ FAILED - Retry {retry_count}/{max_retries}")
                        
                        # Delay before retry
                        if not self.stop_event.wait(getattr(config, 'RETRY_DELAY', 5)):
                            continue
                
                except Exception as e:
                    error_msg = str(e)[:100]
                    
                    # Update GUI - worker card
                    if self.worker_callback:
                        self.worker_callback(worker_id, "ERROR", "#e74c3c", f"Error: {error_msg}")
                    
                    # Log to GUI
                    if self.status_callback:
                        self.status_callback(f"[WORKER #{worker_id}] ⚠ ERROR - {error_msg}")
                    
                    logger.error(f"Worker {worker_id} error: {e}")
                    retry_count += 1
                    
                    if not self.stop_event.wait(getattr(config, 'RETRY_DELAY', 5)):
                        continue
            
            # Worker finished
            worker.stop()
            
            # Update GUI - worker card
            if self.worker_callback:
                self.worker_callback(worker_id, "IDLE", "#555555", "Stopped")
            
            # Log to GUI
            if self.status_callback:
                self.status_callback(f"[WORKER #{worker_id}] Stopped")
            
            logger.info(f"Worker {worker_id} stopped")
        
        # Start thread
        thread = threading.Thread(target=worker_thread, daemon=True)
        thread.start()
        self.active_threads[worker_id] = thread
    
    def stop(self):
        """Stop bot gracefully"""
        if not self.is_running:
            return
        
        logger.info("Stopping bot...")
        if self.status_callback:
            self.status_callback("[STOP] Stopping all workers...")
        
        self.is_running = False
        self.stop_event.set()
        
        # Wait for threads to finish (max 10 seconds)
        start_time = time.time()
        for worker_id, thread in list(self.active_threads.items()):
            remaining = 10 - (time.time() - start_time)
            if remaining > 0:
                thread.join(timeout=remaining)
        
        # Force cleanup
        for worker in self.workers.values():
            worker.stop()
        
        self.workers.clear()
        self.active_threads.clear()
        
        logger.info("Bot stopped successfully")
        if self.status_callback:
            self.status_callback("[SUCCESS] All workers stopped!")
    
    def get_statistics(self) -> dict:
        """
        Get current statistics
        
        Returns:
            Dict dengan statistics
        """
        stats = resource_manager.get_stats()
        stats['active_workers'] = len([w for w in self.workers.values() if hasattr(w, 'is_running') and w.is_running])
        stats['total_tasks_completed'] = self.total_tasks_completed
        stats['total_tasks_failed'] = self.total_tasks_failed
        stats['success_count'] = self.total_tasks_completed
        stats['failed_count'] = self.total_tasks_failed
        stats['blacklisted_ips'] = len(getattr(resource_manager, 'blacklisted_ips', set()))
        return stats
    
    def has_worker(self, worker_id: int) -> bool:
        """
        Check if worker exists and is active
        
        Args:
            worker_id: ID worker yang dicek
            
        Returns:
            True jika worker ada dan aktif
        """
        return worker_id in self.workers and self.workers[worker_id] is not None
    
    def toggle_worker_visibility(self, worker_id: int):
        """
        Toggle browser visibility untuk specific worker
        
        Args:
            worker_id: ID worker yang akan di-toggle
        """
        if worker_id not in self.workers:
            logger.warning(f"Worker {worker_id} not found!")
            if self.status_callback:
                self.status_callback(f"[WARNING] Worker #{worker_id} not found!")
            return
        
        worker = self.workers[worker_id]
        
        # Check if worker has driver
        if not hasattr(worker, 'driver') or worker.driver is None:
            logger.warning(f"Worker {worker_id} has no active browser!")
            if self.status_callback:
                self.status_callback(f"[WARNING] Worker #{worker_id} has no active browser!")
            return
        
        try:
            # Check current visibility state
            if not hasattr(worker, 'is_hidden'):
                worker.is_hidden = True  # Default hidden
            
            if worker.is_hidden:
                # Show browser
                worker.driver.set_window_position(100, 100)
                worker.driver.set_window_size(800, 600)
                worker.is_hidden = False
                logger.info(f"Worker {worker_id}: Browser shown")
                if self.status_callback:
                    self.status_callback(f"[INFO] Worker #{worker_id} browser SHOWN")
            else:
                # Hide browser
                worker.driver.set_window_position(-2400, -2400)
                worker.driver.set_window_size(100, 100)
                worker.is_hidden = True
                logger.info(f"Worker {worker_id}: Browser hidden")
                if self.status_callback:
                    self.status_callback(f"[INFO] Worker #{worker_id} browser HIDDEN")
                
        except Exception as e:
            logger.error(f"Worker {worker_id}: Error toggling visibility - {e}")
            if self.status_callback:
                self.status_callback(f"[ERROR] Worker #{worker_id} visibility toggle failed!")

# Global instance
orchestrator = BotOrchestrator()
