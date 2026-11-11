import pytest
from agent.protocol.schemas import AgentResponse, WriteFileAction, RunCommandAction, ProjectPlan
from agent.protocol.parser import ProtocolParser
from agent.protocol.validator import ProtocolValidator
from agent.protocol.normalizer import ActionNormalizer

def test_protocol_parser_markdown_fence():
    raw = """
Here is the plan:
```json
{
  "version": "1.0",
  "type": "agent_response",
  "summary": "Initial setup",
  "actions": [
    {
      "type": "write_file",
      "path": "server.js",
      "content": "console.log('hi');"
    }
  ],
  "next_task": "Next",
  "requires_user": false
}
```
Done!
    """
    parsed = ProtocolParser.parse_raw_response(raw)
    assert parsed["type"] == "agent_response"
    assert len(parsed["actions"]) == 1

def test_protocol_parser_healing_trailing_commas():
    malformed = '{"version": "1.0", "type": "agent_response", "summary": "Heal test", "actions": [], "requires_user": false, }'
    parsed = ProtocolParser.parse_raw_response(malformed)
    assert parsed["summary"] == "Heal test"

def test_protocol_validator_success():
    data = {
        "version": "1.0",
        "type": "agent_response",
        "summary": "Validated turn",
        "actions": [
            {"type": "run_command", "command": "npm test"}
        ],
        "requires_user": False
    }
    is_valid, resp, err = ProtocolValidator.validate_response(data)
    assert is_valid is True
    assert resp is not None
    assert err is None
    assert resp.actions[0].type == "run_command"

def test_protocol_validator_rejection():
    invalid_data = {
        "type": "agent_response",
        # missing summary
        "actions": [{"type": "unknown_action_type"}]
    }
    is_valid, resp, err = ProtocolValidator.validate_response(invalid_data)
    assert is_valid is False
    assert resp is None
    assert err is not None

def test_action_normalizer():
    action = {
        "type": "write_file",
        "path": "\\src\\components\\App.jsx ",
        "content": "export default App;"
    }
    norm = ActionNormalizer.normalize_action(action)
    assert norm["path"] == "src/components/App.jsx"
