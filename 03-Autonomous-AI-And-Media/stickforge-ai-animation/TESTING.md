# StickForge AI — Testing Guide

## Test Architecture

StickForge AI includes test suites across four primary testing categories:

1. **Unit Tests (`tests/unit/`)**:
   - `test_config.py`: Configuration loading, validation, default fallbacks.
   - `test_database.py`: SQLite migrations, repository CRUD, transaction rollbacks.
   - `test_schema_validator.py`: Storyboard and script schema validation, bad input rejection.
   - `test_character_skeleton.py`: Joint hierarchy, FK matrix calculations, pose bounds.
   - `test_motion_library.py`: Procedural interpolation, walk/run cycle generation.
   - `test_audio_mixer.py`: Ducking logic, stream synchronization, subtitle alignment.
   - `test_task_manager.py`: State machine transitions, checkpoints, bounded retries.

2. **Integration Tests (`tests/integration/`)**:
   - `test_browser_manager.py`: Mocked and local Playwright persistent profile launch, session state checks.
   - `test_deepseek_continue.py`: Multi-segment simulated DeepSeek output, `Continue` button detection, duplicate-click prevention.
   - `test_ffmpeg_compositor.py`: Real deterministic frame generation -> MP4 render -> FFprobe stream verification.
   - `test_publishing_adapters.py`: Mocked OAuth and REST API uploads for YouTube and Instagram.

3. **UI Tests (`tests/ui/`)**:
   - `test_main_window.py`: PySide6 widget initialization, navigation routing, responsive layout.
   - `test_project_wizard.py`: Form validation, project initialization signal flow.

4. **End-to-End Test (`tests/e2e/`)**:
   - `test_full_pipeline.py`: Project creation -> AI generation -> Storyboard -> Frame rendering -> Audio synthesis -> Final MP4 export -> Output verification.

---

## Running Tests

Run all unit and integration tests:
```bash
pytest -v
```

Run specific test modules:
```bash
pytest tests/unit/test_database.py -v
pytest tests/unit/test_character_skeleton.py -v
pytest tests/integration/test_ffmpeg_compositor.py -v
```

Generate coverage report:
```bash
pytest --cov=app tests/
```
