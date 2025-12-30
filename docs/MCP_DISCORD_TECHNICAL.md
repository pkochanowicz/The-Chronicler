# External MCP Server Integration

This document outlines how to connect The Chronicler to an external **Master Control Program (MCP) Server**. The MCP server provides a secure API layer that allows authorized AI agents to interact with the Discord bot's functionality.

The Chronicler is a client of the MCP server. The official MCP server for this project is [discord-guildmaster-mcp](https://github.com/pkochanowicz/discord-guildmaster-mcp).

## Architecture

- **The Chronicler:** Acts as a Discord bot and handles user-facing interactions. It makes API calls to the MCP server for agent-driven actions.
- **MCP Server:** A separate application that exposes high-level bot functions as REST API endpoints. It is responsible for authenticating and executing requests from AI agents.

## Configuration

To connect The Chronicler to an MCP server, you must configure the following environment variables:

- `MCP_SERVER_URL`: The base URL of the running MCP server (e.g., `http://localhost:8080` for local development, or the production URL).
- `MCP_API_KEY`: The secret API key required to authenticate with the MCP server.

These variables are typically stored in your `.env` file for local development or as secrets in your deployment environment (e.g., Fly.io secrets).

### Example `.env` Configuration:
```
MCP_SERVER_URL=http://localhost:8080
MCP_API_KEY=your-secret-api-key
```

## Usage

Once configured, The Chronicler will automatically use the external MCP server for features that rely on AI agent interactions, such as:

- Generating character portraits.
- Performing complex data lookups on behalf of an agent.
- Posting messages or images to specific channels programmatically.

For details on deploying the MCP server itself, please refer to the documentation within the [discord-guildmaster-mcp](https://github.com/pkochanowicz/discord-guildmaster-mcp) repository.
