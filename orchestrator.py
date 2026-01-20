"""
Bot Orchestrator - Central Coordinator V3.1 INTELLIGENT
Mengkoordinasi semua worker dan resource
ENHANCED: Queue System + Auto Retry + URL Tracking + INFINITE LOOP + SHUFFLE MODE
INTELLIGENT: Human-like URL distribution, Anti-detection optimized
"""

import threading
import time
import random
from queue import Queue, Empty
from typing import List, Callable, Set

# Import relative untuk struktur folder yang benar
try:
    from .bot_config import config
    from .worker import BotWorker
    from .resource_manager import resource_manager
except ImportError:
    # Fallback untuk direct import
    from bot_config import config
    from core.worker import BotWorker
    from core.resource_manager import resource_manager

try:
    from utils.logger import logger
    from utils.helpers import read_file_lines
except ImportError:
    # Create simple fallbacks
    import logging
    logger = logging.getLogger(__name__)
    
    def read_file_lines(file_path):
        """Simple file reader fallback"""
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

# Import AI Engine
try:
    from ai.intelligence_engine import ai_engine
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logger.warning("⚠️ AI Engine not available in orchestrator")


class BotOrchestrator:
    """
    Central coordinator untuk semua bot operations
    V3.1 INTELLIGENT: Human-like behavior with shuffle mode + anti-detection
    """

    def __init__(self):
        """Initialize orchestrator"""
        self.workers = {}
        self.active_threads = {}
        self.is_running = False
        self.stop_event = threading.Event()

        # ========== QUEUE SYSTEM ==========
        self.url_queue = Queue()  # Queue untuk URL yang belum diproses
        self.visited_urls = set()  # Set untuk tracking URL yang sudah dikunjungi
        self.failed_urls = {}  # Dict untuk tracking URL yang gagal (url: fail_count)
        self.lock = threading.Lock()  # Lock untuk thread-safe operations

        # URLs and proxies
        self.urls = []
        self.proxies = []

        # Callbacks untuk UI updates
        self.status_callback = None
        self.worker_callback = None

        # Statistics
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        self.active_worker_count = 0
        self.total_cycles = 0  # Hitung berapa kali loop selesai

        # AI training flag
        self.ai_trained = False

        # ========== INTELLIGENT FEATURES (NEW!) ==========
        self.shuffle_mode = getattr(config, 'SHUFFLE_MODE', True)  # Default: ON
        self.last_shuffle_time = None

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
                self.status_callback(f"[INFO] ✅ Loaded {len(self.urls)} URLs from article file")

            # ========== POPULATE QUEUE WITH SHUFFLE ==========
            self._reset_queue()

            # Load proxies (optional)
            if config.FILE_PROXIES:
                self.proxies = read_file_lines(config.FILE_PROXIES)
                logger.info(f"Loaded {len(self.proxies)} proxies")
                if self.status_callback:
                    self.status_callback(f"[INFO] ✅ Loaded {len(self.proxies)} proxies")
            else:
                logger.warning("No proxy file set - running without proxy")
                if self.status_callback:
                    self.status_callback("[WARNING] ⚠️ Running WITHOUT proxy")
                self.proxies = []

            return True

        except Exception as e:
            logger.error(f"Failed to load resources: {e}")
            if self.status_callback:
                self.status_callback(f"[ERROR] Failed to load resources: {e}")
            return False

    def _reset_queue(self):
        """
        Reset queue untuk cycle baru dengan INTELLIGENT SHUFFLE
        HUMAN-LIKE: URLs di-shuffle untuk pattern yang berbeda setiap cycle
        Anti-detection: Sulit diprediksi oleh anti-bot algorithm
        """
        with self.lock:
            # Clear existing queue
            while not self.url_queue.empty():
                try:
                    self.url_queue.get_nowait()
                except Empty:
                    break

            # Clear visited tracking (untuk cycle baru)
            self.visited_urls.clear()
            self.failed_urls.clear()

            # ========== INTELLIGENT SHUFFLE MODE (NEW!) ==========
            if self.shuffle_mode:
                # Copy URLs dan shuffle untuk pattern random
                shuffled_urls = self.urls.copy()
                random.shuffle(shuffled_urls)

                # Add shuffled URLs to queue
                for url in shuffled_urls:
                    self.url_queue.put(url)

                self.last_shuffle_time = time.time()

                cycle_info = f" (Cycle #{self.total_cycles + 1})" if self.total_cycles > 0 else ""
                logger.info(f"🎲 Queue shuffled: {len(shuffled_urls)} URLs in random order{cycle_info}")
                if self.status_callback:
                    self.status_callback(
                        f"[INTELLIGENT] 🎲 Queue shuffled: {len(shuffled_urls)} URLs "
                        f"in random order for human-like behavior{cycle_info}"
                    )
            else:
                # Sequential mode (fallback)
                for url in self.urls:
                    self.url_queue.put(url)

                cycle_info = f" (Cycle #{self.total_cycles + 1})" if self.total_cycles > 0 else ""
                logger.info(f"Queue reset: {len(self.urls)} URLs{cycle_info}")
                if self.status_callback:
                    self.status_callback(f"[INFO] 📋 Queue ready: {len(self.urls)} URLs{cycle_info}")

    def get_next_url(self) -> str:
        """
        Get next URL from queue (thread-safe)
        INFINITE LOOP: Jika queue kosong, reset queue otomatis dengan shuffle baru
        Returns:
            URL string or None if stop_event is set
        """
        try:
            url = self.url_queue.get(block=False)
            return url
        except Empty:
            # ========== QUEUE EMPTY - CHECK IF CYCLE COMPLETE ==========
            if not self.stop_event.is_set():
                # Check if all URLs visited in this cycle
                with self.lock:
                    if len(self.visited_urls) >= len(self.urls):
                        # ========== CYCLE COMPLETE - START NEW CYCLE WITH NEW SHUFFLE ==========
                        self.total_cycles += 1
                        logger.info(f"✅ Cycle #{self.total_cycles} completed! Starting new cycle with fresh shuffle...")
                        if self.status_callback:
                            self.status_callback(
                                f"[SUCCESS] 🔄 Cycle #{self.total_cycles} completed! "
                                f"Completed: {len(self.visited_urls)}/{len(self.urls)} URLs | "
                                f"Starting new cycle with different pattern..."
                            )

                        # Reset queue dengan shuffle baru (pattern berbeda!)
                        self._reset_queue()

                        # Try to get URL again
                        try:
                            url = self.url_queue.get(block=False)
                            return url
                        except Empty:
                            return None
                    else:
                        # Queue kosong tapi belum semua visited (ada URL yang di-retry)
                        return None
            else:
                return None

    def mark_url_visited(self, url: str, success: bool):
        """
        Mark URL as visited (thread-safe)
        Args:
            url: URL yang telah dikunjungi
            success: True jika berhasil, False jika gagal
        """
        with self.lock:
            self.visited_urls.add(url)

            if success:
                # Remove from failed tracking if exists
                if url in self.failed_urls:
                    del self.failed_urls[url]
                self.total_tasks_completed += 1
            else:
                # Track failed URL
                self.failed_urls[url] = self.failed_urls.get(url, 0) + 1
                self.total_tasks_failed += 1

                # Re-queue if not exceeded max failures
                max_url_retries = getattr(config, 'MAX_URL_RETRIES', 2)
                if self.failed_urls[url] < max_url_retries:
                    self.url_queue.put(url)
                    logger.info(f"Re-queued failed URL (attempt {self.failed_urls[url]}/{max_url_retries}): {url[:60]}")

    def get_queue_stats(self) -> dict:
        """Get queue statistics"""
        with self.lock:
            return {
                'total_urls': len(self.urls),
                'remaining': self.url_queue.qsize(),
                'visited': len(self.visited_urls),
                'failed': len([url for url, count in self.failed_urls.items() 
                              if count >= getattr(config, 'MAX_URL_RETRIES', 2)]),
                'cycles': self.total_cycles,
                'shuffle_mode': self.shuffle_mode
            }

    def train_ai_models(self):
        """Train AI models dari historical data (background thread)"""
        if not AI_AVAILABLE:
            return

        if not getattr(config, 'AI_ENABLED', True):
            return

        def training_thread():
            try:
                logger.info("🤖 AI Engine: Starting training process...")
                if self.status_callback:
                    self.status_callback("[AI] 🤖 Training AI models from historical data...")

                # Train AI models
                success = ai_engine.train_from_history(None)

                if success:
                    self.ai_trained = True
                    logger.info("✅ AI Engine: Training completed successfully!")
                    if self.status_callback:
                        self.status_callback("[AI] ✅ AI models trained successfully!")
                else:
                    logger.warning("⚠️ AI Engine: Training skipped (not enough data)")
                    if self.status_callback:
                        self.status_callback("[AI] ⚠️ Not enough historical data for training")

            except Exception as e:
                logger.error(f"❌ AI Engine: Training failed - {e}")
                if self.status_callback:
                    self.status_callback(f"[AI] ❌ Training failed: {e}")

        # Run training in background
        thread = threading.Thread(target=training_thread, daemon=True)
        thread.start()

    def start(self, num_workers: int = None):
        """
        Start bot orchestrator with INTELLIGENT features
        Args:
            num_workers: Jumlah worker (default dari config)
        """
        if self.is_running:
            logger.warning("Bot already running!")
            if self.status_callback:
                self.status_callback("[WARNING] ⚠️ Bot already running!")
            return

        # Load resources
        if not self.load_resources():
            return

        # Train AI models (background)
        if AI_AVAILABLE and getattr(config, 'AI_ENABLED', True) and not self.ai_trained:
            self.train_ai_models()

        # Determine worker count
        if num_workers is None:
            num_workers = min(config.TASK_COUNT, getattr(config, 'MAX_WORKERS', 100))

        mode_info = "INTELLIGENT MODE (Shuffled)" if self.shuffle_mode else "Sequential Mode"
        logger.info(f"Starting bot with {num_workers} workers in {mode_info}...")
        if self.status_callback:
            self.status_callback(
                f"[START] 🚀 Launching {num_workers} workers in {mode_info} | "
                f"INFINITE LOOP until STOP clicked"
            )

        self.is_running = True
        self.stop_event.clear()
        self.active_worker_count = 0
        self.total_cycles = 0

        # Start workers
        for worker_id in range(1, num_workers + 1):
            self._start_worker(worker_id)

        logger.info(f"Bot started with {num_workers} workers!")
        if self.status_callback:
            self.status_callback(
                f"[SUCCESS] ✅ {num_workers} workers started! Running in INFINITE mode "
                f"with human-like behavior until STOP clicked."
            )

    def _start_worker(self, worker_id: int):
        """
        Start single worker thread with INFINITE LOOP + AUTO RESTART
        INTELLIGENT: Each worker acts independently and human-like
        """

        def worker_thread():
            worker = BotWorker(worker_id)
            self.workers[worker_id] = worker

            with self.lock:
                self.active_worker_count += 1

            # Update GUI - worker card status
            if self.worker_callback:
                self.worker_callback(worker_id, "INITIALIZING", "#3498db", "Starting up...")

            # Log to GUI
            if self.status_callback:
                self.status_callback(f"[WORKER #{worker_id}] 🔧 Initialized")

            # ========== INFINITE LOOP - Berjalan terus sampai STOP ==========
            consecutive_errors = 0  # Track consecutive errors untuk stability
            max_consecutive_errors = 5

            while not self.stop_event.is_set():
                try:
                    # ========== GET NEXT URL FROM QUEUE ==========
                    url = self.get_next_url()

                    if url is None:
                        # Queue sedang di-reset atau dalam proses retry
                        # Wait sebentar lalu coba lagi
                        if self.worker_callback:
                            self.worker_callback(worker_id, "WAITING", "#f39c12", "Waiting for next URL...")
                        time.sleep(1)
                        continue

                    # Reset error counter on successful URL retrieval
                    consecutive_errors = 0

                    # Shorten URL for display
                    url_short = url[:60] + "..." if len(url) > 60 else url

                    # Update GUI - worker card with FULL URL
                    if self.worker_callback:
                        self.worker_callback(worker_id, "RUNNING", "#3498db", f"Visiting: {url}")

                    # Log to GUI with SHORT URL + progress
                    queue_stats = self.get_queue_stats()
                    if self.status_callback:
                        cycle_info = f" | Cycle #{queue_stats['cycles'] + 1}" if queue_stats['cycles'] > 0 else ""
                        self.status_callback(
                            f"[WORKER #{worker_id}] 🌐 {url_short}{cycle_info}"
                        )

                    # ========== EXECUTE TASK ==========
                    success = worker.execute_task(url, self.proxies)

                    # ========== MARK URL AS VISITED ==========
                    self.mark_url_visited(url, success)

                    # Get fresh stats
                    queue_stats = self.get_queue_stats()

                    if success:
                        # Update GUI - worker card
                        if self.worker_callback:
                            self.worker_callback(worker_id, "SUCCESS", "#00b894", "Task completed!")

                        # Log to GUI with progress
                        if self.status_callback:
                            cycle_info = f" | Cycle #{queue_stats['cycles'] + 1}" if queue_stats['cycles'] > 0 else ""
                            self.status_callback(
                                f"[WORKER #{worker_id}] ✅ SUCCESS | "
                                f"Progress: {queue_stats['visited']}/{queue_stats['total_urls']}{cycle_info} | "
                                f"Remaining: {queue_stats['remaining']}"
                            )

                        # ========== INTELLIGENT DELAY (Human-like) ==========
                        # Random delay 1-3 seconds untuk natural behavior
                        delay = random.uniform(1, 3)
                        if not self.stop_event.wait(delay):
                            continue

                    else:
                        # Update GUI - worker card
                        if self.worker_callback:
                            self.worker_callback(worker_id, "FAILED", "#e74c3c", "Failed, getting next URL...")

                        # Log to GUI
                        if self.status_callback:
                            cycle_info = f" | Cycle #{queue_stats['cycles'] + 1}" if queue_stats['cycles'] > 0 else ""
                            self.status_callback(
                                f"[WORKER #{worker_id}] ❌ FAILED | "
                                f"Progress: {queue_stats['visited']}/{queue_stats['total_urls']}{cycle_info} | "
                                f"Remaining: {queue_stats['remaining']}"
                            )

                        # ========== AUTO RESTART: Langsung ambil URL baru ==========
                        # Shorter delay for failed tasks
                        delay = random.uniform(1, 2)
                        if not self.stop_event.wait(delay):
                            continue

                except Exception as e:
                    error_msg = str(e)[:100]
                    consecutive_errors += 1

                    # Update GUI - worker card
                    if self.worker_callback:
                        self.worker_callback(worker_id, "ERROR", "#e74c3c", f"Error: {error_msg}")

                    # Log to GUI
                    if self.status_callback:
                        self.status_callback(f"[WORKER #{worker_id}] ⚠️ ERROR - {error_msg}")

                    logger.error(f"Worker {worker_id} error: {e}")

                    # ========== STABILITY CHECK ==========
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Worker {worker_id} too many consecutive errors, pausing...")
                        if self.status_callback:
                            self.status_callback(
                                f"[WORKER #{worker_id}] ⚠️ Too many errors, pausing for 30s..."
                            )
                        # Longer pause for stability
                        if not self.stop_event.wait(30):
                            consecutive_errors = 0  # Reset after pause
                            continue
                    else:
                        # ========== AUTO RESTART: Continue to next URL ==========
                        delay = random.uniform(2, 4)
                        if not self.stop_event.wait(delay):
                            continue

            # ========== WORKER STOPPED (User clicked STOP) ==========
            worker.stop()

            with self.lock:
                self.active_worker_count -= 1

            # Update GUI - worker card
            if self.worker_callback:
                self.worker_callback(worker_id, "IDLE", "#555555", "Stopped")

            # Log to GUI
            if self.status_callback:
                self.status_callback(f"[WORKER #{worker_id}] ⏹️ Stopped by user")

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
            self.status_callback("[STOP] ⏹️ Stopping all workers...")

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

        # Print final stats
        queue_stats = self.get_queue_stats()
        logger.info(f"Bot stopped - Final stats: {queue_stats}")
        if self.status_callback:
            self.status_callback(
                f"[SUCCESS] ✅ All workers stopped! | "
                f"Total completed: {self.total_tasks_completed} | "
                f"Total cycles: {queue_stats['cycles']} | "
                f"Failed: {queue_stats['failed']}"
            )

    def get_statistics(self) -> dict:
        """
        Get current statistics
        Returns:
            Dict dengan statistics
        """
        stats = {}
        
        # Add resource manager stats if available
        try:
            if resource_manager:
                rm_stats = resource_manager.get_stats()
                stats.update(rm_stats)
        except:
            pass
        
        # Add orchestrator stats
        stats['active_workers'] = self.active_worker_count
        stats['total_tasks_completed'] = self.total_tasks_completed
        stats['total_tasks_failed'] = self.total_tasks_failed
        stats['success_count'] = self.total_tasks_completed
        stats['failed_count'] = self.total_tasks_failed
        
        try:
            if resource_manager:
                stats['blacklisted_ips'] = len(getattr(resource_manager, 'blacklisted_ips', set()))
        except:
            stats['blacklisted_ips'] = 0

        # Add queue stats
        queue_stats = self.get_queue_stats()
        stats.update(queue_stats)

        # Add AI training status
        if AI_AVAILABLE:
            stats['ai_trained'] = self.ai_trained
        else:
            stats['ai_trained'] = False

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
        Toggle browser visibility untuk specific worker (BAS-Style)
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
            # Use BAS-style toggle
            worker.toggle_visibility()
            status = "SHOWN 👁️" if not worker.is_hidden else "HIDDEN 🙈"
            logger.info(f"Worker {worker_id}: Browser {status}")
            if self.status_callback:
                self.status_callback(f"[INFO] Worker #{worker_id} browser {status}")
        except Exception as e:
            logger.error(f"Worker {worker_id}: Error toggling visibility - {e}")
            if self.status_callback:
                self.status_callback(f"[ERROR] Worker #{worker_id} visibility toggle failed!")


# Global instance - UNTUK KOMPATIBILITAS
if __name__ == "__main__":
    orchestrator = BotOrchestrator()
else:
    orchestrator = None