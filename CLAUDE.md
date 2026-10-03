# Claude Code Configuration

## Filesystem Access Control

**CRITICAL: Strict access limitation**

### Allowed Paths
- ✅ `/Users/cicianid/Projects/aws-lakehouse-poc` - Full read/write access
- ✅ `/Users/cicianid/Projects/aws-lakehouse-poc/.claude` - Memory and config
- ✅ Subdirectories: `python/`, `scripts/`, `infra/`, `data/`, `tests/`, `reports/`

### Blocked Paths
- ❌ `/Users` - Home directory (except /Users/cicianid/Projects/aws-lakehouse-poc)
- ❌ `/Users/cicianid` - Home directory
- ❌ `/Users/cicianid/.Trash` - Trash directory
- ❌ `/Users/cicianid/Library` - Library directory
- ❌ `/tmp` - Temporary files
- ❌ `/var` - System directories
- ❌ `/` - Root directory
- ❌ Any path outside this project

### Enforcement
- Do NOT execute `find`, `ls`, `cd` outside allowed paths
- Do NOT use glob patterns that expand outside allowed paths
- Do NOT create symlinks outside allowed paths
- Do NOT read environment variables to discover other paths
- Do NOT attempt to access parent directories (`../`)

## Commands Behavior

### Allowed
- `git` operations within repo
- `cat`, `grep`, `sed` on files in repo
- `aws` CLI for AWS operations (pre-authorized)
- Python scripts execution

### Blocked
- Filesystem exploration outside repo
- Accessing user home files
- Reading system configuration
- Modifying git remote configuration destructively

## File Operations Rules

### Before deleting files
- MUST ask for explicit confirmation
- MUST describe what will be deleted and why
- MUST wait for user approval
- NO automatic cleanup without permission

### Before modifying .gitignore, .git, or git config
- MUST ask permission first
- MUST explain the changes

## Error Handling

If you encounter an access denied error or permission issue:
1. Stop immediately
2. Explain the issue clearly
3. Ask for permission to proceed
4. Do NOT attempt workarounds or use different paths

## Violation Policy

Violating these rules results in:
- Immediate restriction of access
- Loss of trust on this project
- Potential termination of work on this codebase

---

**Last Updated:** 2026-10-03
**Status:** ACTIVE - Enforced
