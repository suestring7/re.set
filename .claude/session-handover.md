# Session Handover — re.set MVVM 重构

_最后更新：2026-05-10_

---

## 背景

re.set 是一个 macOS 菜单栏休息提醒 App。原始代码是约 1600 行的 `break_reminder.py` 单体文件（PyObjC + WKWebView + 内嵌 HTTP 服务器）。

本系列 session 的目标是将其重构为 **Python MVVM 架构**，同时保持跨平台可移植性（macOS 现在，Windows 未来）。重构策略是增量式：原始单体文件在整个过程中保持可运行，模块逐步提取。

最近两个 session 的重心是：把重构后的代码实际跑起来（`main_macos.py` 入口 + py2app 打包），并修复运行时 bug。

---

## 已完成的事

### MVVM 核心层（完整实现）

```
core/models/          app_config.py, checkin.py, daily_record.py, exercise.py, activity_type.py
core/services/        persistence.py, exercise_service.py, scoring.py
core/timer/           break_timer.py
core/viewmodels/      app_viewmodel.py, records_viewmodel.py, preferences_viewmodel.py
core/utils/           date_helpers.py, observable.py
```

### macOS 平台层（完整实现）

```
platforms/macos/      adapter.py, controller.py, http_server.py
main_macos.py         入口文件（替代 break_reminder.py）
```

### UI 文件（全部迁移至 ui/ 目录）

```
ui/break_reminder_ui.html, records_ui.html, away_form.html, return_form.html,
ui/preferences.html, warning.html, plan_today.html, shared.js,
ui/exercises.json, activity_types.json
```

### 本 session 修复的 Bug

#### Bug 1：菜单项全部灰掉（只有 Quit 可用）

- **根因**：`platforms/macos/controller.py` 中 NSMenuItem 的 action 字符串写成了 `"handlePause_:"` 格式。PyObjC 把 `def handlePause_(self, sender)` 注册为 ObjC selector `handlePause:`（去掉下划线前的冒号），两者不匹配，`respondsToSelector:` 返回 NO，macOS 自动禁用所有项。
- **修复**：把 controller.py 中全部 14 处 selector 字符串从 `method_:` 改为 `method:` 格式。
- **验证方法**：`target.respondsToSelector_('handlePause_:')` → False；`target.respondsToSelector_('handlePause:')` → True

#### Bug 2：定时器到点不弹窗口

- **根因**：`AppViewModel` 的 `show_break_window` 和 `show_warning_panel` 是 `Observable[bool]` 字段，但平台层从未订阅。Timer 触发 → AppViewModel 设置 `show_break_window.value = True` → 没有任何代码收到通知。
- **修复**：在 `applicationDidFinishLaunching_` 中调用新增的 `_setup_subscriptions()` 方法，订阅两个 Observable，通过 `performSelectorOnMainThread` 派发到主线程执行 UI 操作。

#### Bug 3：安装的 .app 启动报错

- **根因**：`~/Applications/re.set.app` 里的 `python314.zip` 包含旧编译的 `.pyc`，早于所有 `@objc.python_method` 修复，启动时抛 `BadPrototypeError`。
- **修复**：重新运行 `bash packaging/build_app.sh` 后重装。

### 文档更新

- `CLAUDE.md` — 新建，记录了 PyObjC selector 约定、Observable 订阅规则、`@objc.python_method` 用法、构建流程、依赖方向等关键约定。

---

## 关键决策

| 决策 | 原因 |
|------|------|
| `core/` 不得有任何 OS 导入 | 跨平台可移植性；Windows 版本未来只需替换 `platforms/windows/` |
| Observable 用轻量 callback 实现，不引入第三方 reactive 库 | 避免依赖、减少打包体积；Python 没有原生 Combine/Flow |
| `performSelectorOnMainThread` 派发 UI 操作 | AppKit 要求所有 UI 操作在主线程；HTTP handler 线程和 timer 线程都是非主线程 |
| `@objc.python_method` 装饰所有私有辅助方法 | 避免 PyObjC 把不符合 ObjC arity 约定的方法注册为 selector，防止 `BadPrototypeError` |
| py2app 打包用自定义 codesign 替代默认流程 | Python 3.14 + macOS 15+ 下默认的逐文件重签名会失败；改为先 strip 所有签名再统一 ad-hoc 重签 |
| `plan_today.html` 用 10 分钟倒计时 + 关键字写入外部文件 | 用户需要把今日计划追加到现有笔记文件（Obsidian 等），而不是 re.set 自己的记录系统 |

---

## 未解决的问题

### 功能验证未完成

以下功能在最新构建中**尚未人工验证**：

1. **Plan Today 窗口** — `preferences.html` 的 Plan 标签页配置文件路径和关键字后，Plan Today 是否能正确写入目标文件。
2. **Preferences Features 标签页** — 菜单功能开关（toggle）是否即时生效并持久化。
3. **定时器到点弹窗流程** — 等待一个完整计时周期（或用"Trigger Break Now"）确认 Observable 订阅修复有效。
4. **Return Log 双记录原子写入** — 离开模式返回时的 `commit_return_log()` 流程。
5. **Warning Panel 推迟（postpone）流程** — 最多推迟 3 次，每次 +5 分钟。

### 代码层面的未跟踪问题

- `showWarningPanel:` 和 `hideWarningPanel:` 这两个 ObjC selector 在 `controller.py` 中**是否已实现**，需要确认（session 中修复了订阅代码，但没有逐行确认这两个方法存在）。
- `git status` 显示 `ui/plan_today.html` 等多个文件处于 untracked 状态，从未 commit 过。

---

## 下一步

新 session 建议按以下顺序推进：

1. **验证已修复的 bug**：启动 `~/Applications/re.set.app`，逐一点击所有菜单项，确认不再灰掉；用 "Trigger Break Now" 测试弹窗。

2. **确认 `showWarningPanel:`/`hideWarningPanel:` 存在**：
   ```bash
   grep -n "showWarningPanel\|hideWarningPanel" platforms/macos/controller.py
   ```
   若不存在，需要实现这两个方法。

3. **完整功能测试**：
   - Preferences → Plan 标签页：配置文件路径 + 关键字 → Plan Today → 保存，检查目标文件。
   - Preferences → Features 标签页：关闭某个菜单项，重启后确认仍关闭。
   - Away mode 完整流程：Pause → 离开 → Return → 确认双记录写入。

4. **提交所有未 commit 的文件**：
   ```bash
   git add ui/ platforms/ core/ main_macos.py setup.py CLAUDE.md
   git commit -m "complete MVVM refactor and fix PyObjC selector bugs"
   ```

5. **（可选）Phase 5**：实现 `RecordsViewModel` 的 edit/delete + delta focus-minutes 逻辑（见 HACKING.md 或 plan 文件）。

---

## 需要知道的上下文

### 项目结构

```
re.set/
├── core/                   纯 Python，零 OS 导入
│   ├── models/
│   ├── services/
│   ├── timer/
│   ├── utils/
│   └── viewmodels/
├── platforms/macos/        PyObjC 平台层
├── ui/                     HTML/JS，两平台共用
├── main_macos.py           当前入口（替代 break_reminder.py）
├── break_reminder.py       原始单体，保留作参考
├── setup.py                py2app 构建（自定义 codesign）
└── packaging/build_app.sh  构建 + 安装脚本
```

### PyObjC Selector 陷阱（必须记住）

```python
# Python 方法名里的 trailing _ 会变成 ObjC selector 里的 :
def handlePause_(self, sender): ...   # → ObjC selector: handlePause:

# NSMenuItem / NSTimer / performSelectorOnMainThread 里的字符串必须用 ObjC 格式
_item("暂停", "handlePause:", target=self)   # 正确
_item("暂停", "handlePause_:", target=self)  # 错误，会导致菜单项灰掉
```

### 构建命令

```bash
bash packaging/build_app.sh
# 等价于：
python setup.py py2app 2>&1 | tail -20
rm -rf ~/Applications/re.set.app
cp -R dist/re.set.app ~/Applications/
```

每次修改 Python 源码后必须重新构建，`.app` 里的 `.pyc` 不会自动更新。

### HTTP 服务器端口

`localhost:18030`，所有 HTML/JS 通过此端口与后端通信。

### 参考计划文件

完整的 MVVM 重构方案见：`~/.claude/plans/glowing-gathering-perlis.md`（在 Claude 会话中通过 Plan 模式生成）。
