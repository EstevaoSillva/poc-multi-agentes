"""
Tool registry and broker - centralized tool management with sandboxing and access control.

Provides:
- ToolRegistry: Register and catalog all available tools
- ToolBroker: Execute tools with sandbox checks, auditoria, and access gates
- Policies: Permission and safety checks per session/intent
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
from multiprocessing import Process, Queue
import traceback

logger = logging.getLogger(__name__)


class ToolPermission(str, Enum):
    """Tool permission levels."""
    PUBLIC = "public"  # Anyone can use
    SESSION = "session"  # Only within session context
    DESTRUCTIVE = "destructive"  # Requires approval
    ADMIN = "admin"  # Admin only


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    description: str
    category: str  # "file", "code", "project", "ai", etc
    permission: ToolPermission
    requires_approval: bool = False
    sandbox_required: bool = True
    max_timeout_sec: int = 30
    arg_schema: Optional[Dict] = None  # JSON schema for args


@dataclass
class ToolExecutionRecord:
    """Record of a tool execution for audit trail."""
    tool_name: str
    session_id: int
    user_id: Optional[str]
    args: Dict
    result: Any
    status: str  # "success", "error", "blocked"
    error_message: Optional[str] = None
    timestamp: str = ""
    execution_time_ms: float = 0.0


class ToolRegistry:
    """
    Centralized registry of all available tools.
    
    Maintains:
    - Tool metadata (name, description, permissions)
    - Tool implementations
    - Permission matrix
    """

    def __init__(self):
        self.tools: Dict[str, Dict] = {}  # name -> {metadata, callable}
        self.permissions: Dict[str, ToolPermission] = {}

    def register(
        self,
        name: str,
        impl: Callable,
        description: str,
        category: str,
        permission: ToolPermission = ToolPermission.PUBLIC,
        requires_approval: bool = False,
        sandbox_required: bool = True,
        max_timeout_sec: int = 30,
        arg_schema: Optional[Dict] = None,
    ) -> None:
        """
        Register a tool.
        
        Args:
            name: Tool identifier (e.g., "read_file", "write_file")
            impl: Callable that implements the tool
            description: Human-readable description
            category: Tool category
            permission: Permission level (public/session/destructive/admin)
            requires_approval: Requires user approval before execution
            sandbox_required: Must run in sandbox
            max_timeout_sec: Max execution time
            arg_schema: JSON schema for arguments validation
        """
        metadata = ToolMetadata(
            name=name,
            description=description,
            category=category,
            permission=permission,
            requires_approval=requires_approval,
            sandbox_required=sandbox_required,
            max_timeout_sec=max_timeout_sec,
            arg_schema=arg_schema,
        )

        self.tools[name] = {
            "metadata": metadata,
            "callable": impl,
        }

        self.permissions[name] = permission
        logger.info(f"Registered tool: {name} (permission: {permission})")

    def get(self, name: str) -> Optional[Dict]:
        """Get tool by name."""
        return self.tools.get(name)

    def list_tools(
        self,
        category: Optional[str] = None,
        permission: Optional[ToolPermission] = None,
    ) -> List[ToolMetadata]:
        """List available tools with optional filters."""
        results = []
        for tool in self.tools.values():
            meta = tool["metadata"]
            if category and meta.category != category:
                continue
            if permission and meta.permission != permission:
                continue
            results.append(meta)
        return results

    def to_dict(self) -> Dict:
        """Export registry as dict (for API responses)."""
        return {
            name: {
                "metadata": asdict(tool["metadata"]),
                "description": tool["metadata"].description,
            }
            for name, tool in self.tools.items()
        }


class ToolBroker:
    """
    Tool execution broker with sandboxing and access control.
    
    Handles:
    - Permission checks (can user execute this tool?)
    - Sandbox enforcement (is execution safe?)
    - Argument validation
    - Execution with timeout
    - Audit logging
    - Approval gates for destructive operations
    """

    def __init__(
        self,
        registry: ToolRegistry,
        session_id: int,
        workspace_path: Path,
        user_id: Optional[str] = None,
    ):
        self.registry = registry
        self.session_id = session_id
        self.workspace_path = workspace_path
        self.user_id = user_id
        self.execution_log: List[ToolExecutionRecord] = []

    def can_execute(
        self,
        tool_name: str,
        user_intent: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if tool can be executed by this session/user.
        
        Args:
            tool_name: Tool to check
            user_intent: User's declared intent (for context)
        
        Returns:
            (can_execute, reason_if_blocked)
        """
        tool = self.registry.get(tool_name)
        if not tool:
            return False, f"Tool not found: {tool_name}"

        metadata = tool["metadata"]

        # Check permission level
        if metadata.permission == ToolPermission.ADMIN:
            return False, "Tool requires admin permission"

        if metadata.permission == ToolPermission.DESTRUCTIVE:
            # Destructive tools require explicit approval
            return True, None  # Caller should gate with approval flow

        return True, None

    def execute(
        self,
        tool_name: str,
        args: Dict,
        user_intent: Optional[str] = None,
        approved: bool = False,
    ) -> tuple[Any, ToolExecutionRecord]:
        """
        Execute a tool with sandbox and audit.
        
        Args:
            tool_name: Tool to execute
            args: Tool arguments
            user_intent: User's declared intent
            approved: Whether user approved execution (for destructive tools)
        
        Returns:
            (result, audit_record)
        """
        from datetime import datetime
        import time

        tool = self.registry.get(tool_name)
        if not tool:
            record = ToolExecutionRecord(
                tool_name=tool_name,
                session_id=self.session_id,
                user_id=self.user_id,
                args=args,
                result=None,
                status="blocked",
                error_message="Tool not found",
                timestamp=datetime.utcnow().isoformat(),
            )
            self.execution_log.append(record)
            return None, record

        metadata = tool["metadata"]
        callable_impl = tool["callable"]

        # Permission check
        can_exec, reason = self.can_execute(tool_name, user_intent)
        if not can_exec:
            record = ToolExecutionRecord(
                tool_name=tool_name,
                session_id=self.session_id,
                user_id=self.user_id,
                args=args,
                result=None,
                status="blocked",
                error_message=reason,
                timestamp=datetime.utcnow().isoformat(),
            )
            self.execution_log.append(record)
            logger.warning(f"Tool blocked: {tool_name} - {reason}")
            return None, record

        # Destructive check
        if metadata.permission == ToolPermission.DESTRUCTIVE and not approved:
            record = ToolExecutionRecord(
                tool_name=tool_name,
                session_id=self.session_id,
                user_id=self.user_id,
                args=args,
                result=None,
                status="blocked",
                error_message="Destructive tool requires approval",
                timestamp=datetime.utcnow().isoformat(),
            )
            self.execution_log.append(record)
            logger.info(f"Tool requires approval: {tool_name}")
            return None, record

        # Argument validation
        if metadata.arg_schema:
            valid, err = self._validate_args(args, metadata.arg_schema)
            if not valid:
                record = ToolExecutionRecord(
                    tool_name=tool_name,
                    session_id=self.session_id,
                    user_id=self.user_id,
                    args=args,
                    result=None,
                    status="blocked",
                    error_message=f"Argument validation failed: {err}",
                    timestamp=datetime.utcnow().isoformat(),
                )
                self.execution_log.append(record)
                logger.warning(f"Arg validation failed for {tool_name}: {err}")
                return None, record

        # Sandbox check (optional)
        if metadata.sandbox_required:
            safe, sandbox_reason = self._check_sandbox(tool_name, args)
            if not safe:
                record = ToolExecutionRecord(
                    tool_name=tool_name,
                    session_id=self.session_id,
                    user_id=self.user_id,
                    args=args,
                    result=None,
                    status="blocked",
                    error_message=f"Sandbox violation: {sandbox_reason}",
                    timestamp=datetime.utcnow().isoformat(),
                )
                self.execution_log.append(record)
                logger.warning(f"Sandbox violation: {tool_name} - {sandbox_reason}")
                return None, record
        # Execute tool with timeout in a separate process to enforce max_timeout
        start_time = time.time()
        result = None
        error_msg = None
        status = "success"

        def _proc_runner(func, kwargs, out_q: Queue):
            try:
                res = func(**kwargs)
                out_q.put((True, res))
            except Exception as e:
                tb = traceback.format_exc()
                out_q.put((False, tb))

        out_q: Queue = Queue()
        proc = Process(target=_proc_runner, args=(callable_impl, args, out_q))
        proc.start()
        proc.join(metadata.max_timeout_sec)

        if proc.is_alive():
            proc.terminate()
            proc.join()
            status = "error"
            error_msg = f"Tool execution timed out after {metadata.max_timeout_sec}s"
            logger.error(error_msg)
        else:
            # retrieve result
            try:
                ok, payload = out_q.get_nowait()
                if ok:
                    result = payload
                else:
                    status = "error"
                    error_msg = payload
                    logger.error(f"Tool execution raised: {payload}")
            except Exception:
                status = "error"
                error_msg = "Tool returned no output"
                logger.error("Tool returned no output")

        execution_time_ms = (time.time() - start_time) * 1000

        # Audit record
        record = ToolExecutionRecord(
            tool_name=tool_name,
            session_id=self.session_id,
            user_id=self.user_id,
            args=args,
            result=result,
            status=status,
            error_message=error_msg,
            timestamp=datetime.utcnow().isoformat(),
            execution_time_ms=execution_time_ms,
        )

        self.execution_log.append(record)
        return result, record

    def _check_sandbox(self, tool_name: str, args: Dict) -> tuple[bool, Optional[str]]:
        """
        Check sandbox constraints (e.g., file path boundaries).
        
        Returns:
            (is_safe, reason_if_unsafe)
        """
        # File operation tools
        if tool_name in ["read_file", "write_file", "delete_file"]:
            path_arg = args.get("path")
            if not path_arg:
                return False, "Missing path argument"

            target = (self.workspace_path / path_arg).resolve()
            root = self.workspace_path.resolve()

            if not str(target).startswith(str(root)):
                return False, f"Path outside workspace: {target}"

            if tool_name == "delete_file":
                # prevent deleting directories or workspace root
                if target == root:
                    return False, "Refusing to delete workspace root"
                if target.is_dir():
                    return False, "Refusing to delete a directory"

        if tool_name == "list_files":
            base = args.get("base_path") or args.get("path")
            if not base:
                return False, "Missing base_path/path argument"
            target = (self.workspace_path / base).resolve()
            root = self.workspace_path.resolve()
            if not str(target).startswith(str(root)):
                return False, f"Path outside workspace: {target}"
            if not target.exists():
                return False, f"Base path does not exist: {target}"

        return True, None

    def _validate_args(self, args: Dict, schema: Dict) -> tuple[bool, Optional[str]]:
        """
        Lightweight argument validator.

        Schema format (simple): {"arg_name": "str|int|dict|list|bool"}
        """
        for k, t in schema.items():
            if k not in args:
                return False, f"Missing required arg: {k}"
            val = args[k]
            if t == "str" and not isinstance(val, str):
                return False, f"Arg {k} must be str"
            if t == "int" and not isinstance(val, int):
                return False, f"Arg {k} must be int"
            if t == "dict" and not isinstance(val, dict):
                return False, f"Arg {k} must be dict"
            if t == "list" and not isinstance(val, list):
                return False, f"Arg {k} must be list"
            if t == "bool" and not isinstance(val, bool):
                return False, f"Arg {k} must be bool"
        return True, None

    def get_execution_log(self) -> List[ToolExecutionRecord]:
        """Get execution audit trail."""
        return self.execution_log

    def export_audit(self) -> Dict:
        """Export audit trail as dict."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "executions": [asdict(record) for record in self.execution_log],
            "total_executions": len(self.execution_log),
            "successful": len([r for r in self.execution_log if r.status == "success"]),
            "blocked": len([r for r in self.execution_log if r.status == "blocked"]),
            "errors": len([r for r in self.execution_log if r.status == "error"]),
        }


# Singleton registry (can be extended to support multiple registries)
_DEFAULT_REGISTRY = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get default tool registry."""
    return _DEFAULT_REGISTRY


def create_broker(
    session_id: int,
    workspace_path: Path,
    user_id: Optional[str] = None,
    registry: Optional[ToolRegistry] = None,
) -> ToolBroker:
    """
    Factory function to create a tool broker.
    
    Args:
        session_id: Session ID
        workspace_path: Session workspace root
        user_id: Optional user identifier
        registry: Tool registry (uses default if None)
    
    Returns:
        ToolBroker instance
    """
    reg = registry or get_tool_registry()
    return ToolBroker(reg, session_id, workspace_path, user_id)
