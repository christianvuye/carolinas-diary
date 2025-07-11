import time
import logging
from fastapi import Request
from typing import Callable, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, slow_request_threshold: float = 0.5, very_slow_threshold: float = 2.0):
        """
        Initialize performance monitor with configurable thresholds
        
        Args:
            slow_request_threshold: Time in seconds to consider a request slow (default: 0.5s)
            very_slow_threshold: Time in seconds to consider a request very slow (default: 2.0s)
        """
        self.slow_request_threshold = slow_request_threshold
        self.very_slow_threshold = very_slow_threshold
    
    async def monitor_request(self, request: Request, call_next: Callable):
        """
        Middleware function to monitor request performance
        
        Args:
            request: FastAPI Request object
            call_next: Next middleware or endpoint function
            
        Returns:
            Response from the next middleware/endpoint
        """
        start_time = time.time()
        
        # Extract request details for logging
        method = request.method
        url_path = request.url.path
        query_params = str(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        
        try:
            # Process the request
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log performance metrics
            self._log_performance_metrics(
                method=method,
                url_path=url_path,
                query_params=query_params,
                client_ip=client_ip,
                duration=duration,
                status_code=response.status_code,
                success=True
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error with performance metrics
            self._log_performance_metrics(
                method=method,
                url_path=url_path,
                query_params=query_params,
                client_ip=client_ip,
                duration=duration,
                status_code=500,
                success=False,
                error=str(e)
            )
            
            # Re-raise the exception
            raise
    
    def _log_performance_metrics(self, method: str, url_path: str, query_params: str, 
                                client_ip: str, duration: float, status_code: int, 
                                success: bool, error: Optional[str] = None):
        """
        Log performance metrics with appropriate log levels
        
        Args:
            method: HTTP method
            url_path: Request URL path
            query_params: Query parameters
            client_ip: Client IP address
            duration: Request duration in seconds
            status_code: HTTP status code
            success: Whether the request was successful
            error: Error message if request failed
        """
        # Create log message
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url_path": url_path,
            "query_params": query_params,
            "client_ip": client_ip,
            "duration": round(duration, 3),
            "status_code": status_code,
            "success": success
        }
        
        if error:
            log_data["error"] = error
        
        # Determine log level based on duration and success
        if not success:
            logger.error(f"Request failed: {json.dumps(log_data)}")
        elif duration >= self.very_slow_threshold:
            logger.error(f"Very slow request detected: {json.dumps(log_data)}")
        elif duration >= self.slow_request_threshold:
            logger.warning(f"Slow request detected: {json.dumps(log_data)}")
        else:
            logger.info(f"Request completed: {json.dumps(log_data)}")
        
        # Additional alert for very slow requests
        if duration >= self.very_slow_threshold:
            logger.critical(
                f"🚨 CRITICAL: Very slow request detected! "
                f"{method} {url_path} took {duration:.2f}s "
                f"(threshold: {self.very_slow_threshold}s) - "
                f"Client: {client_ip}"
            )

# Create a global instance for easy access
performance_monitor = PerformanceMonitor()

# Convenience function to get the middleware
def get_performance_middleware():
    """
    Returns the performance monitoring middleware function
    
    Usage:
        app.add_middleware(BaseHTTPMiddleware, dispatch=performance_monitor.monitor_request)
    """
    return performance_monitor.monitor_request