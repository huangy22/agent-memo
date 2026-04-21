# Agent Memory Skills Library

这不是一个让最终用户手动执行 `run.sh` 的工具包。  
它的目标形态是一组可安装到 agent 环境里的 skills：

- `memory-note`
- `memory-reflect`
- `memory-distill`
- `memory-status`

安装完成后，用户应该直接在 `Codex` / `Claude Code` 里调用这些 skill，而不是自己手动拼底层命令。

## 用户会怎么用

装好以后，正常使用方式应该是：

- `#memory-status`
- `#memory-note`
- `#memory-reflect`
- `#memory-distill`

也就是说，这个仓库提供的是一个 `skills library`。  
`run.sh`、本地 CLI、runtime 都只是 skill 内部实现细节。

## 安装到 Codex

把这套 skills 安装到 `Codex` 的 skills 目录：

```bash
bash install.sh --codex --execute
```

这会把内容安装到：

```bash
~/.codex/skills/
```

安装完成后，你应该能在 skills 目录里看到：

- `memory-note/`
- `memory-reflect/`
- `memory-distill/`
- `memory-status/`

## 安装到 Claude Code

把这套 skills 安装到 `Claude Code` 的 skills 目录：

```bash
bash install.sh --claude --execute
```

这会把内容安装到：

```bash
~/.claude/skills/
```

## 自定义安装目录

如果你的 agent 环境使用自定义 skill library 目录，可以手动指定：

```bash
bash install.sh --target /path/to/skills --execute
```

只有这种情况才需要自己传 `--target`。  
对大多数用户，直接用 `--codex` 或 `--claude` 即可。

## `--execute` 是什么

安装脚本默认是 dry-run。  
也就是说，不加 `--execute` 时，它只会打印将要安装到哪里，不会真的写文件。

例如：

```bash
bash install.sh --codex
```

这适合先检查目标目录。  
确认无误后再执行真正安装：

```bash
bash install.sh --codex --execute
```

## 安装后用户需要知道什么

用户只需要知道两件事：

1. 这几个 skills 已经装进 agent 的 skill library
2. 在对话里直接调用 `#memory-status`、`#memory-note`、`#memory-reflect`、`#memory-distill`

用户不需要手动运行这些内部文件：

- `run.sh`
- `agent-memory-*`
- `.agent-memory-runtime/`

这些都是 skills 的内部实现。

## 这些 skills 做什么

### `memory-status`

查看当前仓库的记忆状态，包括：

- 项目级 memory 文件是否存在
- short-term trace 是否存在
- reflect / distill request bundle 是否存在

### `memory-note`

记录一次任务中的具体修复或决策，写入 short-term trace。

### `memory-reflect`

把最近的 short-term trace 反思为项目级 memory。

### `memory-distill`

把项目级 memory 整理成可以推广到更广范围的候选条目。

## 数据写到哪里

安装发生在 agent 的 skill 目录里。  
真正的记忆数据不写在 skill 目录，而是写在你当前工作的目标仓库里：

```bash
<repo>/.agent-memory/
```

也就是说：

- skill library 放在 `~/.codex/skills/` 或 `~/.claude/skills/`
- 每个项目自己的记忆内容放在该项目自己的 `.agent-memory/`

## 升级

重新执行同样的安装命令到同一个 skills 目录即可。  
如果后续要支持更平滑的覆盖升级，可以在安装脚本里补充 `--force` 或 upgrade 模式；当前版本默认更保守，避免无提示覆盖已有路径。

## 卸载

如果要移除这套 skills，删除对应 skill 目录和内部 runtime 即可。

例如在 Codex：

```bash
rm -rf ~/.codex/skills/memory-note
rm -rf ~/.codex/skills/memory-reflect
rm -rf ~/.codex/skills/memory-distill
rm -rf ~/.codex/skills/memory-status
rm -rf ~/.codex/skills/.agent-memory-runtime
rm -rf ~/.codex/skills/bin
```

这不会删除任何项目仓库里的 `.agent-memory/` 数据。  
如果你还想删除某个项目本身的记忆，再单独删那个仓库下的 `.agent-memory/`。

## 实现说明

这套 library 的产品表面是 skills。  
本地 CLI 和 `run.sh` 的职责只是为 skills 提供稳定 runtime，不是给最终用户作为主入口。
