# 🤖 AI Agent · CLI · MCP 가이드

레이디안은 GUI만 자동 클릭하는 방식보다 **안전하고 구조화된 CLI/MCP**를 우선 제공합니다. Computer Use 에이전트도 `data-testid`, 의미 있는 버튼/레이블, 키보드 동작을 활용할 수 있어요.

## CLI 실행

```bash
node bin/raidian.cjs --repo /path/to/repository --json status
node bin/raidian.cjs --repo /path/to/repository log --limit 10
node bin/raidian.cjs --repo /path/to/repository commit
node bin/raidian.cjs --repo /path/to/repository merge chatgpt-extrahigh/feature/one --yes
node bin/raidian.cjs --repo /path/to/repository remote-add backup https://github.com/owner/repo.git
node bin/raidian.cjs --repo /path/to/repository --json agent-guide
```

- 최상위 `--repo`, `--json`은 명령 앞뒤 모두 허용됩니다.
- CLI의 이력 변경 명령 `merge`, `copy-commit`, `revert`, `remote-remove`, `gh-pr-create`에는 `--yes` 필요.
- `shell`은 사람이 읽는 대화형 인터페이스, `--json`은 프로그램/LLM 에이전트에게 적합합니다.
- CLI `doctor`는 Git·gh 경로와 Node/Electron 런타임을 조회합니다.

## MCP stdio

```bash
# 읽기 전용
node bin/raidian-mcp.cjs --repo /path/to/repository
# 제한된 쓰기 도구 사용
node bin/raidian-mcp.cjs --repo /path/to/repository --allow-write
```

호환 프로토콜: `initialize` = `2025-11-25`, `server/discover` = `2026-07-28`, `tools/list`, `tools/call`, `ping`. JSON-RPC 메시지는 **한 줄에 하나**만 입력하고 서버 응답도 stdout 한 줄 JSON입니다. 진단 오류는 stderr로 보냅니다.

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"sample","version":"1"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"git_status","arguments":{}}}
```

쓰기 예시 (`--allow-write` 실행 시):

```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"git_commit","arguments":{"message":"docs: 사용 설명서 보완","confirm":true}}}
```

도구 이름은 `git_status`, `git_log`, `git_branch_child`, `git_merge`, `git_copy_commit`, `git_revert`, `git_remote_add`, `git_gh_prs` 등입니다. `tools/list`가 실제 사용 가능한 도구 목록의 기준입니다. **MCP는 임의 셸 명령 실행/force-push를 지원하지 않으며**, 허용한 단일 저장소로만 접근합니다. `confirm:true`는 호출 인자이며 사람 승인의 증명 수단이 아닙니다. 신뢰할 수 없는 에이전트에는 쓰기 모드를 열지 마세요.

## GUI 자동화

| 동작 | 안정적인 셀렉터 |
|---|---|
| 저장소 열기 | `[data-testid="open-repo"]` |
| 저장소 경로 확인 | `[data-testid="repository-path"]` |
| 커밋 입력 | `[data-testid="commit-message"]` |
| 커밋 + 푸시 | `[data-testid="commit-push"]` |
| 새 브랜치 | `[data-testid="branch-create"]` |
| 이력 | `[data-testid="history-list"]` |
| 상태 알림 | `#status[role=status]`의 상위 footer |

UI 구조를 직접 조작해 destructive action을 우회하려고 하지 말고 CLI/MCP 쓰기와 확인 절차를 따르세요.
