"""
Logging module for MCP Pizza
Logs all two-way interactions between the MCP server and clients
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Setup logging directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger("mcpizza")
logger.setLevel(logging.DEBUG)

# File handler for all interactions
interaction_log = LOG_DIR / f"interactions_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(interaction_log)
file_handler.setLevel(logging.DEBUG)

# Console handler for errors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class InteractionLogger:
    """Logger for MCP interactions"""

    @staticmethod
    def log_tool_call(tool_name: str, arguments: dict, request_id: Optional[str] = None):
        """Log incoming tool call"""
        log_data = {
            "type": "tool_call",
            "direction": "incoming",
            "tool_name": tool_name,
            "arguments": arguments,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"TOOL_CALL | {json.dumps(log_data)}")

    @staticmethod
    def log_tool_response(tool_name: str, success: bool, response: Any,
                         request_id: Optional[str] = None, error: Optional[str] = None):
        """Log outgoing tool response"""
        # Truncate large responses for logging
        response_preview = str(response)[:500] if response else None

        log_data = {
            "type": "tool_response",
            "direction": "outgoing",
            "tool_name": tool_name,
            "success": success,
            "response_preview": response_preview,
            "request_id": request_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"TOOL_RESPONSE | {json.dumps(log_data)}")

    @staticmethod
    def log_tool_list_request():
        """Log tools/list request"""
        log_data = {
            "type": "list_tools",
            "direction": "incoming",
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"LIST_TOOLS | {json.dumps(log_data)}")

    @staticmethod
    def log_initialization(client_info: dict):
        """Log MCP initialization"""
        log_data = {
            "type": "initialization",
            "direction": "incoming",
            "client_info": client_info,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"INIT | {json.dumps(log_data)}")

    @staticmethod
    def log_error(error_type: str, error_message: str, context: Optional[dict] = None):
        """Log errors"""
        log_data = {
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"ERROR | {json.dumps(log_data)}")

    @staticmethod
    def log_state_change(state_type: str, old_value: Any, new_value: Any):
        """Log state changes (e.g., order creation, items added)"""
        log_data = {
            "type": "state_change",
            "state_type": state_type,
            "old_value": str(old_value)[:200] if old_value else None,
            "new_value": str(new_value)[:200] if new_value else None,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"STATE_CHANGE | {json.dumps(log_data)}")


# Global instance
interaction_logger = InteractionLogger()
