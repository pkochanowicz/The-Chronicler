# MCP-Discord Technical Documentation

This document provides instructions on how to install and use the `mcp/mcp-discord` Docker image for local development and testing. This server enables AI assistants to interact with the Discord platform.

## Installation

We will use Docker to run the `mcp-discord` server. This is the recommended approach for local development as it isolates the server and its dependencies.

### Prerequisites

- Docker installed and running on your local machine.

### Running the Docker Container

To run the `mcp-discord` server, execute the following command in your terminal:

```bash
docker run -d --name mcp-discord -p 8080:8080 mcp/mcp-discord
```

This command will:

- `-d`: Run the container in detached mode (in the background).
- `--name mcp-discord`: Assign a name to the container for easier management.
- `-p 8080:8080`: Map port 8080 of the host machine to port 8080 of the container. This makes the server accessible at `http://localhost:8080`.
- `mcp/mcp-discord`: The name of the Docker image to run.

## Usage

Once the server is running, you can interact with it by sending HTTP requests to `http://localhost:8080`. The server exposes a set of tools that can be used to interact with Discord.

For detailed information on the available tools and their usage, please refer to the official documentation of the `mcp-discord` project.

## Development and Testing

For development and testing purposes, you can use this server to allow LLM-based agents to interact directly with your Discord server. This is useful for testing new commands and features without deploying the main application.

**Important:** This setup is intended for local development and testing only. It should not be used in a production environment.
