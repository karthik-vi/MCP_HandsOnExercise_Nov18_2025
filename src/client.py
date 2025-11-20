import asyncio
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def connect_to_weather_server():
    """
    Launches your FastMCP server as a subprocess and connects via STDIO.
    """
    server_params = StdioServerParameters(
        command="python",          # or "python3" if needed
        args=["weather_server.py"],  # path to your server script
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # MCP handshake / capability negotiation
            await session.initialize()
            yield session


async def demo_calls():
    async with connect_to_weather_server() as session:
        # Discover tools exposed by your FastMCP server
        tools_response = await session.list_tools()
        print("Available tools:", [t.name for t in tools_response.tools])

        # --- Call get_alerts(state: str) ---
        print("\n=== get_alerts('NY') ===")
        alerts_result = await session.call_tool(
            "get_alerts",  # tool name = function name
            arguments={"state": "NY"},
        )

        first_block = alerts_result.content[0]
        if isinstance(first_block, types.TextContent):
            print(first_block.text)
        else:
            print(alerts_result)

        # --- Call get_forecast(latitude: float, longitude: float) ---
        print("\n=== get_forecast(42.9, -78.8) ===  # Buffalo-ish")
        forecast_result = await session.call_tool(
            "get_forecast",
            arguments={"latitude": 42.9, "longitude": -78.8},
        )

        first_block = forecast_result.content[0]
        if isinstance(first_block, types.TextContent):
            print(first_block.text)
        else:
            print(forecast_result)


def main():
    asyncio.run(demo_calls())


if __name__ == "__main__":
    main()
