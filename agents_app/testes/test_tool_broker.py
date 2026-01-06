"""
Test suite for ToolRegistry and ToolBroker.
"""

import tempfile
from pathlib import Path
from agents_app.tools.tool_broker import (
    ToolRegistry,
    ToolBroker,
    ToolPermission,
    create_broker,
    get_tool_registry,
)
from agents_app.tools.tool_registration import register_default_tools


def test_tool_registry():
    """Test ToolRegistry functionality."""
    print("\n" + "=" * 60)
    print("Testing ToolRegistry")
    print("=" * 60)
    
    registry = ToolRegistry()
    
    # Register a test tool
    def dummy_read(path):
        return f"content of {path}"
    
    registry.register(
        name="test_read",
        impl=dummy_read,
        description="Test read tool",
        category="file",
        permission=ToolPermission.PUBLIC,
    )
    
    print("✓ Registered test_read tool")
    
    # List tools
    tools = registry.list_tools(category="file")
    print(f"✓ Found {len(tools)} file tools")
    
    # Get tool
    tool = registry.get("test_read")
    assert tool is not None
    print(f"✓ Retrieved tool: {tool['metadata'].name}")
    
    return True


def test_tool_broker():
    """Test ToolBroker sandboxing and permissions."""
    print("\n" + "=" * 60)
    print("Testing ToolBroker")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create broker
        broker = create_broker(
            session_id=1,
            workspace_path=workspace,
            user_id="test_user",
        )
        
        print("✓ Created ToolBroker")
        
        # Check default tools
        registry = get_tool_registry()
        tools = registry.list_tools()
        print(f"✓ Default registry has {len(tools)} tools")
        
        # List available tools by permission
        public_tools = registry.list_tools(permission=ToolPermission.PUBLIC)
        destructive_tools = registry.list_tools(permission=ToolPermission.DESTRUCTIVE)
        
        print(f"  - Public: {len(public_tools)} tools")
        print(f"  - Destructive: {len(destructive_tools)} tools")
        
        # Test permission check
        can_read, reason = broker.can_execute("read_file")
        assert can_read, f"Should be able to read files: {reason}"
        print("✓ Read tool is accessible")
        
        can_delete, reason = broker.can_execute("delete_file")
        assert can_delete, f"Should be able to delete (requires approval): {reason}"
        print("✓ Delete tool requires approval (not blocked at can_execute)")
        
        # Test sandbox check
        safe, msg = broker._check_sandbox("read_file", {"path": "test.txt"})
        assert safe, f"Should be safe: {msg}"
        print("✓ Safe path passes sandbox check")
        
        safe, msg = broker._check_sandbox("read_file", {"path": "../../../etc/passwd"})
        assert not safe, "Should block directory traversal"
        print("✓ Directory traversal blocked by sandbox")
        
        # Test audit log
        audit = broker.export_audit()
        assert audit["total_executions"] == 0, "No executions yet"
        print(f"✓ Audit log initialized (0 executions)")
        
        return True


def test_destructive_gate():
    """Test destructive tool gating."""
    print("\n" + "=" * 60)
    print("Testing Destructive Tool Gating")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        broker = create_broker(session_id=1, workspace_path=workspace)
        
        # Define a dummy delete tool
        registry = get_tool_registry()
        def dummy_delete(path):
            return f"deleted {path}"
        
        registry.register(
            name="test_delete",
            impl=dummy_delete,
            description="Test delete",
            category="file",
            permission=ToolPermission.DESTRUCTIVE,
            requires_approval=True,
        )
        
        # Try to execute without approval
        result, record = broker.execute("test_delete", {"path": "test.txt"}, approved=False)
        assert result is None, "Should be blocked"
        assert record.status == "blocked", "Status should be blocked"
        assert "requires approval" in record.error_message.lower()
        print("✓ Destructive tool blocked without approval")
        
        # Execute with approval
        result, record = broker.execute("test_delete", {"path": "test.txt"}, approved=True)
        assert record.status == "success", "Should succeed with approval"
        print("✓ Destructive tool allowed with approval")
        
        # Check audit
        audit = broker.export_audit()
        assert audit["total_executions"] == 2, "Should have 2 executions"
        assert audit["blocked"] == 1, "Should have 1 blocked"
        assert audit["successful"] == 1, "Should have 1 successful"
        print(f"✓ Audit log: {audit['successful']} success, {audit['blocked']} blocked")
        
        return True


if __name__ == "__main__":
    try:
        test_tool_registry()
    except Exception as e:
        print(f"✗ ToolRegistry test failed: {e}")
        raise
    
    try:
        test_tool_broker()
    except Exception as e:
        print(f"✗ ToolBroker test failed: {e}")
        raise
    
    try:
        test_destructive_gate()
    except Exception as e:
        print(f"✗ Destructive gate test failed: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("✓ All ToolBroker tests passed!")
    print("=" * 60)
