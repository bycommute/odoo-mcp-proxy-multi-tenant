#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import FastMCP
from mcp.server.fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP(name="test", json_response=False, stateless_http=False)

# Test tool 1
@mcp.tool()
async def tool1():
    """Tool 1"""
    return "tool1"

# Test tool 2
@mcp.tool()
async def tool2():
    """Tool 2"""
    return "tool2"

# Test tool 3 (defined after others)
@mcp.tool()
async def tool3():
    """Tool 3"""
    return "tool3"

# Print tools
print(f"Total tools registered: {len(mcp._fastmcp.tools)}")
for tool_name in mcp._fastmcp.tools:
    print(f"  - {tool_name}")

