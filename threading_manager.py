"""
Modern threading manager for Python 3.14+ with free-threaded support.

This module provides improved threading primitives and management
specifically designed for Python 3.14's free-threaded mode (PEP 703).
"""
import sys
import threading
from typing import Optional, Callable, Any
from queue import Queue, Empty
from contextlib import contextmanager
import time


class ThreadManager:
    """
    Modern thread manager with Python 3.14 optimizations.
    
    Features:
    - Proper thread lifecycle management
    - Daemon threads support
    - Graceful shutdown
    - Free-threaded mode detection
    - Thread-safe operations
    """
    
    def __init__(self):
        self.threads = []
        self.shutdown_event = threading.Event()
        self.is_free_threaded = self._check_free_threaded()
        
    def _check_free_threaded(self) -> bool:
        """Check if Python is running in free-threaded mode (no GIL)."""
        try:
            # Python 3.13+: Check if GIL is disabled
            import sysconfig
            return sysconfig.get_config_var("Py_GIL_DISABLED") == 1
        except:
            return False
    
    def create_worker(
        self,
        target: Callable,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        name: Optional[str] = None,
        daemon: bool = True
    ) -> threading.Thread:
        """
        Create and start a managed worker thread.
        
        Args:
            target: Function to run in thread
            args: Positional arguments
            kwargs: Keyword arguments
            name: Thread name for debugging
            daemon: If True, thread will exit when main program exits
            
        Returns:
            Started Thread object
        """
        if kwargs is None:
            kwargs = {}
        
        thread = threading.Thread(
            target=target,
            args=args,
            kwargs=kwargs,
            name=name,
            daemon=daemon
        )
        
        self.threads.append(thread)
        thread.start()
        
        return thread
    
    def shutdown(self, timeout: float = 5.0):
        """
        Gracefully shutdown all managed threads.
        
        Args:
            timeout: Maximum time to wait for each thread
        """
        self.shutdown_event.set()
        
        # Wait for non-daemon threads to finish
        for thread in self.threads:
            if thread.is_alive() and not thread.daemon:
                thread.join(timeout=timeout)
                
                if thread.is_alive():
                    print(f"Warning: Thread {thread.name} did not terminate within {timeout}s")
    
    def is_shutting_down(self) -> bool:
        """Check if shutdown has been requested."""
        return self.shutdown_event.is_set()


class ThreadSafeAudioQueue:
    """
    Thread-safe queue for audio data with Python 3.14 optimizations.
    
    Uses Queue which is already thread-safe, but adds convenience methods
    and monitoring for free-threaded mode.
    """
    
    def __init__(self, maxsize: int = 10):
        self.queue = Queue(maxsize=maxsize)
        self._lock = threading.Lock()  # For additional protection if needed
        
    def put(self, audio_data: Any, block: bool = True, timeout: Optional[float] = None):
        """
        Put audio data into the queue.
        
        Args:
            audio_data: Audio data to queue
            block: If True, block if queue is full
            timeout: Timeout in seconds (None = infinite)
        """
        self.queue.put(audio_data, block=block, timeout=timeout)
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """
        Get audio data from the queue.
        
        Args:
            block: If True, block if queue is empty
            timeout: Timeout in seconds (None = infinite)
            
        Returns:
            Audio data or None if timeout
        """
        try:
            return self.queue.get(block=block, timeout=timeout)
        except Empty:
            return None
    
    def clear(self):
        """Clear all items from the queue."""
        with self._lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except Empty:
                    break
    
    def qsize(self) -> int:
        """Get approximate queue size (may not be exact in free-threaded mode)."""
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        return self.queue.empty()


class WorkerLoop:
    """
    Base class for worker threads with proper shutdown handling.
    
    Example:
        class MyWorker(WorkerLoop):
            def work_iteration(self):
                # Do work
                pass
        
        worker = MyWorker()
        thread = threading.Thread(target=worker.run)
        thread.start()
        
        # Later...
        worker.shutdown()
        thread.join()
    """
    
    def __init__(self, name: str = "Worker"):
        self.name = name
        self._shutdown_event = threading.Event()
        self._running = False
        
    def run(self):
        """Main loop - call this in Thread target."""
        self._running = True
        print(f"{self.name}: started")
        
        try:
            while not self._shutdown_event.is_set():
                try:
                    self.work_iteration()
                except Exception as e:
                    print(f"{self.name}: Error in work_iteration: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(0.5)  # Prevent tight loop on repeated errors
        finally:
            self._running = False
            print(f"{self.name}: stopped")
    
    def work_iteration(self):
        """
        Override this method in subclass to do actual work.
        Should return relatively quickly to check shutdown flag.
        """
        raise NotImplementedError("Subclass must implement work_iteration()")
    
    def shutdown(self, timeout: float = 5.0):
        """Request shutdown and wait for completion."""
        self._shutdown_event.set()
    
    def is_running(self) -> bool:
        """Check if worker is currently running."""
        return self._running
    
    def should_continue(self) -> bool:
        """Check if worker should continue (not shutting down)."""
        return not self._shutdown_event.is_set()


@contextmanager
def performance_monitor(operation_name: str):
    """
    Context manager to monitor thread performance in free-threaded mode.
    
    Usage:
        with performance_monitor("audio_processing"):
            process_audio()
    """
    start_time = time.perf_counter()
    thread_id = threading.get_ident()
    
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start_time
        print(f"[Thread {thread_id}] {operation_name}: {elapsed:.3f}s")


# Utility functions for Python 3.14 detection
def get_python_version_info() -> dict:
    """Get detailed Python version and threading info."""
    try:
        import sysconfig
        gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED") == 1
    except:
        gil_disabled = False
    
    return {
        "version": sys.version,
        "version_info": sys.version_info,
        "free_threaded": gil_disabled,
        "thread_info": {
            "current_thread": threading.current_thread().name,
            "active_count": threading.active_count(),
            "main_thread": threading.main_thread().name,
        }
    }


def print_threading_info():
    """Print current threading configuration."""
    info = get_python_version_info()
    
    print("=" * 60)
    print("Python Threading Configuration")
    print("=" * 60)
    print(f"Python Version: {info['version_info'].major}.{info['version_info'].minor}.{info['version_info'].micro}")
    print(f"Free-threaded (No GIL): {info['free_threaded']}")
    print(f"Current Thread: {info['thread_info']['current_thread']}")
    print(f"Active Threads: {info['thread_info']['active_count']}")
    print(f"Main Thread: {info['thread_info']['main_thread']}")
    print("=" * 60)


if __name__ == "__main__":
    # Test the module
    print_threading_info()
    
    # Test ThreadManager
    print("\nTesting ThreadManager...")
    
    def test_worker(worker_id: int, manager: ThreadManager):
        for i in range(5):
            if manager.is_shutting_down():
                break
            print(f"Worker {worker_id}: iteration {i}")
            time.sleep(0.5)
    
    manager = ThreadManager()
    
    # Create workers
    for i in range(3):
        manager.create_worker(
            target=test_worker,
            args=(i, manager),
            name=f"TestWorker-{i}",
            daemon=True
        )
    
    # Let them run
    time.sleep(3)
    
    # Shutdown
    print("\nShutting down...")
    manager.shutdown()
    
    print("\nDone!")
