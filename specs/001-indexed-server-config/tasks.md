# Tasks: Indexed Server Configuration

**Input**: Design documents from `/specs/001-indexed-server-config/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Testing is explicitly required per constitution check (Testing Priorities section). This feature includes comprehensive test tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Project root is `/home/jgato/Projects-src/my_github/prometheus-alerts-mcp/`
- Main file: `prometheus_mcp.py` (modification)
- Tests: `tests/` directory (new)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and testing infrastructure

- [x] T001 Add pytest dependency to requirements.txt
- [x] T002 Create tests/ directory structure with __init__.py
- [x] T003 [P] Create tests/conftest.py with shared fixtures (mock_env, reset_servers, sample_server_config)
- [x] T004 [P] Create tests/test_config_loading.py test file skeleton with test classes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Remove old configuration loading code from prometheus_mcp.py (lines ~38-66: PROMETHEUS_SERVERS and PROMETHEUS_URL/TOKEN logic)
- [ ] T006 Create helper function parse_verify_ssl() in prometheus_mcp.py for boolean/string parsing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Configure Multiple Servers with Individual Variables (Priority: P1) 🎯 MVP

**Goal**: Load servers from indexed environment variables PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9, supporting gaps in numbering

**Independent Test**: Set PROMETHEUS_SERVER_0, PROMETHEUS_SERVER_1, etc. and verify list_servers tool shows all configured servers correctly

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T007 [P] [US1] Write test_single_server_at_index_0 in tests/test_config_loading.py
- [ ] T008 [P] [US1] Write test_multiple_servers_sequential in tests/test_config_loading.py  
- [ ] T009 [P] [US1] Write test_three_servers_configured in tests/test_config_loading.py
- [ ] T010 [P] [US1] Write test_servers_with_gaps in tests/test_config_loading.py (indices 1, 3)
- [ ] T011 [P] [US1] Write test_all_10_servers_configured in tests/test_config_loading.py
- [ ] T012 [P] [US1] Write test_only_index_9_configured in tests/test_config_loading.py

### Implementation for User Story 1

- [ ] T013 [US1] Implement environment variable scanning loop (range 0-9) in load_servers() function in prometheus_mcp.py
- [ ] T014 [US1] Implement gap handling logic (continue on missing indices) in load_servers() function in prometheus_mcp.py
- [ ] T015 [US1] Implement basic JSON parsing with try/except for each variable in load_servers() function in prometheus_mcp.py
- [ ] T016 [US1] Build SERVERS dictionary from successfully parsed configs in load_servers() function in prometheus_mcp.py

**Checkpoint**: Run test suite for US1 - all 6 tests should pass. Verify list_servers tool works with various configurations.

---

## Phase 4: User Story 2 - Individual Server Configuration Format (Priority: P1)

**Goal**: Support all server configuration fields (name, url, description, token, verify_ssl) with proper validation and defaults

**Independent Test**: Set PROMETHEUS_SERVER_0 with various field combinations and verify all fields are correctly parsed and defaults applied

### Tests for User Story 2

- [ ] T017 [P] [US2] Write test_all_fields_present in tests/test_config_loading.py
- [ ] T018 [P] [US2] Write test_only_required_fields in tests/test_config_loading.py
- [ ] T019 [P] [US2] Write test_verify_ssl_false in tests/test_config_loading.py
- [ ] T020 [P] [US2] Write test_verify_ssl_string_formats in tests/test_config_loading.py (test "true", "false", "yes", "1")
- [ ] T021 [P] [US2] Write test_missing_required_field_name in tests/test_config_loading.py
- [ ] T022 [P] [US2] Write test_missing_required_field_url in tests/test_config_loading.py

### Implementation for User Story 2

- [ ] T023 [US2] Implement required field validation (name, url) in load_servers() function in prometheus_mcp.py
- [ ] T024 [US2] Implement optional field default application (description="", token="", verify_ssl=True) in load_servers() function in prometheus_mcp.py
- [ ] T025 [US2] Integrate parse_verify_ssl() helper function for verify_ssl field parsing in load_servers() function in prometheus_mcp.py
- [ ] T026 [US2] Add field type validation and coercion in load_servers() function in prometheus_mcp.py

**Checkpoint**: Run test suite for US2 - all 6 tests should pass. Verify servers with various field combinations load correctly.

---

## Phase 5: User Story 3 - Clear Error Messages for Configuration Issues (Priority: P2)

**Goal**: Provide clear, actionable error messages for invalid configurations while continuing to load valid servers

**Independent Test**: Configure invalid server at PROMETHEUS_SERVER_0 and valid at PROMETHEUS_SERVER_1, verify warning logged and valid server loads

### Tests for User Story 3

- [ ] T027 [P] [US3] Write test_missing_url_field_warning in tests/test_config_loading.py
- [ ] T028 [P] [US3] Write test_invalid_json_warning in tests/test_config_loading.py
- [ ] T029 [P] [US3] Write test_duplicate_server_names in tests/test_config_loading.py
- [ ] T030 [P] [US3] Write test_invalid_verify_ssl_warning in tests/test_config_loading.py
- [ ] T031 [P] [US3] Write test_out_of_range_index_10_warning in tests/test_config_loading.py
- [ ] T032 [P] [US3] Write test_out_of_range_index_15_warning in tests/test_config_loading.py
- [ ] T033 [P] [US3] Write test_multiple_invalid_servers_continue_loading in tests/test_config_loading.py

### Implementation for User Story 3

- [ ] T034 [US3] Add JSON parse error handling with descriptive warnings in load_servers() function in prometheus_mcp.py
- [ ] T035 [US3] Add missing required field warnings with field name in load_servers() function in prometheus_mcp.py
- [ ] T036 [US3] Implement duplicate name detection and warning in load_servers() function in prometheus_mcp.py
- [ ] T037 [US3] Add invalid verify_ssl value warning and default to True in parse_verify_ssl() function in prometheus_mcp.py
- [ ] T038 [US3] Implement out-of-range index detection (check indices 10-99) and warnings in load_servers() function in prometheus_mcp.py
- [ ] T039 [US3] Ensure graceful continuation after errors (skip invalid, load others) in load_servers() function in prometheus_mcp.py

**Checkpoint**: Run test suite for US3 - all 7 tests should pass. Verify clear warnings for each error type and valid servers still load.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [ ] T040 [P] Update README.md with indexed configuration examples (remove old PROMETHEUS_URL and PROMETHEUS_SERVERS sections)
- [ ] T041 [P] Add configuration troubleshooting section to README.md
- [ ] T042 [P] Add zero-based indexing explanation to README.md
- [ ] T043 [P] Remove servers-config-example.json file (no longer needed)
- [ ] T044 Run full test suite (all 19 tests) and verify 100% pass
- [ ] T045 Test with real Prometheus server using list_servers tool
- [ ] T046 [P] Add code comments explaining indexed scanning logic in prometheus_mcp.py
- [ ] T047 Validate quickstart.md examples work correctly
- [ ] T048 Update constitution.md if multi-server architecture description needs adjustment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 and 2 (both P1) can proceed in parallel after Foundational
  - User Story 3 (P2) can start after Foundational, may benefit from US1 completion for context
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable (uses same load_servers function)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 with error handling

**Note**: US1 and US2 share the same `load_servers()` function, so while logically separate user stories, implementation is interleaved in the same file. US2 adds field validation on top of US1's scanning logic.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation tasks execute in order listed
- Story complete and all tests passing before moving to next priority

### Parallel Opportunities

- **Phase 1**: All 4 setup tasks can run in parallel (T001-T004)
- **Phase 2**: T005 and T006 are sequential (T006 uses cleaned code from T005)
- **User Story 1 Tests**: All 6 test tasks (T007-T012) can run in parallel
- **User Story 2 Tests**: All 6 test tasks (T017-T022) can run in parallel
- **User Story 3 Tests**: All 7 test tasks (T027-T033) can run in parallel
- **Phase 6**: T040-T043 and T046 can run in parallel (different files)

**Team Strategy**: With 2 developers after Foundational:
- Developer A: User Story 1 + tests
- Developer B: User Story 2 + tests  
- Then merge and collaborate on User Story 3

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all test writing tasks together:
Task T007: "Write test_single_server_at_index_0 in tests/test_config_loading.py"
Task T008: "Write test_multiple_servers_sequential in tests/test_config_loading.py"
Task T009: "Write test_three_servers_configured in tests/test_config_loading.py"
Task T010: "Write test_servers_with_gaps in tests/test_config_loading.py"
Task T011: "Write test_all_10_servers_configured in tests/test_config_loading.py"
Task T012: "Write test_only_index_9_configured in tests/test_config_loading.py"

# All can be written in parallel since each is a separate test function
```

---

## Parallel Example: Polish Phase

```bash
# Launch documentation tasks together:
Task T040: "Update README.md with indexed configuration examples"
Task T041: "Add configuration troubleshooting section to README.md"
Task T042: "Add zero-based indexing explanation to README.md"
Task T043: "Remove servers-config-example.json file"
Task T046: "Add code comments in prometheus_mcp.py"

# All can be done in parallel - different sections/files
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

Both User Story 1 and 2 are Priority P1 and share implementation in `load_servers()`:

1. Complete Phase 1: Setup (pytest infrastructure)
2. Complete Phase 2: Foundational (remove old code, add helper)
3. Complete Phase 3: User Story 1 (basic indexed loading + tests)
4. Complete Phase 4: User Story 2 (field validation + tests)
5. **STOP and VALIDATE**: Test both US1 and US2 independently
6. Deploy/demo if ready - core functionality complete

**At this checkpoint you have**:
- ✅ Indexed server configuration working
- ✅ All field combinations supported
- ✅ 12 tests passing
- ✅ MVP deployable

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T006)
2. Add User Story 1 → Test independently (T007-T016) → Basic loading works
3. Add User Story 2 → Test independently (T017-T026) → Full field support
4. **Deploy/Demo MVP** (core functionality complete)
5. Add User Story 3 → Test independently (T027-T039) → Error handling complete
6. Polish Phase → Documentation and cleanup (T040-T048)
7. **Final Release**

### Parallel Team Strategy

With 2 developers:

**Week 1: Setup + Foundation**
- Both: Complete Phase 1 and 2 together (T001-T006)

**Week 2: Core Functionality (P1)**
- Developer A: User Story 1 tests and implementation (T007-T016)
- Developer B: User Story 2 tests and implementation (T017-T026)
- **Sync**: Merge US1 and US2 into load_servers(), resolve any conflicts
- **Checkpoint**: Test both stories work together

**Week 3: Enhancement (P2) + Polish**
- Developer A: User Story 3 tests and implementation (T027-T039)
- Developer B: Polish phase documentation (T040-T043, T046-T048)
- **Final Test**: Run full test suite (T044-T045)

---

## Test Coverage Summary

| User Story | Test Count | Purpose |
|------------|-----------|---------|
| US1 (P1) | 6 tests | Basic indexed loading, gaps, all 10 servers |
| US2 (P1) | 6 tests | Field validation, defaults, verify_ssl formats |
| US3 (P2) | 7 tests | Error handling for all invalid config scenarios |
| **Total** | **19 tests** | **Comprehensive coverage** |

### Test Execution Time Estimate
- Setup: ~1 hour to write fixtures
- US1 tests: ~2 hours to write all 6
- US2 tests: ~2 hours to write all 6  
- US3 tests: ~2.5 hours to write all 7
- **Total**: ~7.5 hours of test writing

### Implementation Time Estimate
- Setup + Foundational: ~3 hours
- US1 implementation: ~3 hours
- US2 implementation: ~2 hours
- US3 implementation: ~6 hours
- Polish: ~3 hours
- **Total**: ~17 hours of implementation

**Grand Total**: ~24.5 hours (matches plan.md estimate of 20-22 hours with buffer)

---

## Edge Cases Covered by Tests

From spec.md edge cases, all covered in tests:

✅ **Gaps in indexing** (T010) - SERVER_0, SERVER_3, SERVER_7
✅ **Out-of-range indices** (T031, T032) - SERVER_10, SERVER_15
✅ **Empty or invalid name** (T021, T029) - Handled via required field validation
✅ **JSON parsing errors** (T028) - Invalid JSON syntax
✅ **Missing required fields** (T021, T022) - name or url missing
✅ **Single server only** (T007) - PROMETHEUS_SERVER_0 alone
✅ **All 10 servers** (T011) - Maximum capacity test

---

## Success Criteria Mapping

From spec.md Success Criteria, validated by tasks:

- **SC-001**: Configuration time reduced (T040-T042 documentation simplifies setup)
- **SC-002**: Readability improved (indexed vars per quickstart.md, validated T047)
- **SC-003**: Modification time reduced (separate vars enable quick token changes)
- **SC-004**: Error messages actionable (T034-T039 implement clear warnings, T027-T033 test them)
- **SC-005**: First-attempt success rate (T040-T042 documentation + T047 quickstart validation)

---

## Notes

- [P] tasks = different files or test functions, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable (checkpoints define this)
- Verify all tests fail before implementing (TDD approach)
- Commit after each completed task
- Stop at any checkpoint to validate story independently
- Total task count: 48 tasks (19 tests + 29 implementation/docs)
- Parallel opportunities: 18 tasks marked [P] can run simultaneously with others
- MVP scope: Phases 1-4 (User Stories 1 & 2) = ~12 hours of work

