---
name: arifos-mcp-call
description: Invoke arifOS constitutional MCP tools (000-999 pipeline)
user-invocable: true
---

# arifOS MCP Caller

Use the `arifos` CLI bridge to call constitutional tools:

```bash
arifos health          # health check
arifos list            # list all 13 tools
arifos anchor          # 000 - boot session
arifos reason          # 333 - AGI reasoning
arifos memory <query>  # 555 - vector memory search
arifos judge           # 888 - constitutional verdict
arifos seal            # 999 - seal to VAULT999
arifos search <query>  # search reality (multi-source)
arifos audit           # floor audit
```

Or call HTTP directly:
```bash
curl -s http://arifosmcp_server:8080/health | jq
curl -s -X POST http://arifosmcp_server:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

When using constitutional tools, always run anchor_session first to establish context, then proceed through the pipeline as appropriate for the task depth.
