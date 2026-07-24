#!/usr/bin/env bash
# tmuxctl.sh — tmux-orchestrator 플러그인의 결정적 CLI
#
# 실행 중인 claude pane 을 발견·태깅·관측·dispatch 하는 tmux 조작을 캡슐화한다.
# 스킬/에이전트는 tmux 플래그를 직접 다루지 않고 이 서브커맨드만 호출한다.
#
# 서브커맨드:
#   discover [--json]                        claude pane 목록(역할·프로파일·상태 포함)
#   tag      <target> k=v ...                pane user-option 각인 (role/model/attitude/effort/permission/budget/status/task)
#   read     <target> [lines]                pane 화면/스크롤백 출력
#   ready    <target>                        유휴(스피너 부재 & 프롬프트 존재) 시 exit 0
#   send     <target> <file>                 파일 내용을 원자적 주입 후 제출
#   wait     <target> <marker> [timeout]     마커 출력까지 폴링 (0=발견,1=timeout,2=blocked)
#   apply-profile <target> <preset|k=v ...>  기존 pane 에 프로파일 부분 적용(model+fast+tag, effort/permission 경고)
#   spawn    <session> <count> <preset|k=v>  프로파일대로 claude pane 자동 생성
#   preset   <name>                          프리셋을 옵션 문자열로 전개(디버그)
#
# 상태는 tmux pane user-option(@agent-*)에 저장한다. 외부 파일 없음.
set -euo pipefail

# ── 판정 정규식 (claude TUI 버전 변동 시 여기만 조정) ──────────────────────
SPINNER_RE='esc to interrupt|Cogitat|Thinking|Pondering|Working'   # busy 신호
PROMPT_RE='│ >|❯|auto mode'                                        # 입력 프롬프트 존재 신호
POLL_INTERVAL="${TMUXCTL_POLL_INTERVAL:-3}"                        # wait 폴링 주기(초)
WORKER_CMD_RE="${TMUXCTL_WORKER_CMD_RE:-^(claude)$}"               # 워커로 인정할 pane_current_command (env 오버라이드 가능)

err() { printf '%s\n' "tmuxctl: $*" >&2; }
die() { err "$*"; exit 1; }

require_tmux() { command -v tmux >/dev/null 2>&1 || die "tmux 미설치"; }

# ── preset <name> → "model effort permission budget fast attitude" ──────────
# 값이 '-' 이면 해당 옵션 미설정(예: fast).
expand_preset() {
  case "$1" in
    economy) echo "haiku low manual - - economy" ;;
    speed)   echo "sonnet medium acceptEdits - - speed" ;;
    quality) echo "opus high acceptEdits - - quality" ;;
    prose)   echo "fable medium acceptEdits - - prose" ;;
    *)       return 1 ;;
  esac
}

# ── 프로파일 인자 파싱: 첫 토큰이 프리셋명이면 전개 후, k=v 로 override ─────
# 결과를 전역 PF_* 에 채운다.
parse_profile() {
  PF_MODEL="" PF_EFFORT="" PF_PERMISSION="" PF_BUDGET="" PF_FAST="" PF_ATTITUDE="custom"
  local first="${1:-}"
  if base="$(expand_preset "$first" 2>/dev/null)"; then
    set -- "${@:2}"
    read -r PF_MODEL PF_EFFORT PF_PERMISSION PF_BUDGET PF_FAST PF_ATTITUDE <<<"$base"
    [ "$PF_BUDGET" = "-" ] && PF_BUDGET=""
    [ "$PF_FAST" = "-" ] && PF_FAST=""
  fi
  local kv
  for kv in "$@"; do
    case "$kv" in
      model=*)      PF_MODEL="${kv#model=}" ;;
      effort=*)     PF_EFFORT="${kv#effort=}" ;;
      permission=*) PF_PERMISSION="${kv#permission=}" ;;
      budget=*)     PF_BUDGET="${kv#budget=}" ;;
      fast=*)       PF_FAST="${kv#fast=}" ;;
      attitude=*)   PF_ATTITUDE="${kv#attitude=}" ;;
      *) err "무시된 인자: $kv" ;;
    esac
  done
}

cmd_preset() {
  [ $# -ge 1 ] || die "usage: preset <name>"
  expand_preset "$1" || die "알 수 없는 프리셋: $1 (economy|speed|quality|prose)"
}

# ── discover ────────────────────────────────────────────────────────────────
cmd_discover() {
  local json=0; [ "${1:-}" = "--json" ] && json=1
  # 필드 구분자 = Unit Separator(0x1F). 탭은 whitespace 라 read 가 연속 빈 필드를 병합하므로 non-whitespace 사용.
  local US; US=$'\x1f'
  local fmt; fmt="#{pane_current_command}${US}#{session_name}:#{window_index}.#{pane_index}${US}#{pane_pid}${US}#{@agent-role}${US}#{@agent-model}${US}#{@agent-attitude}${US}#{@agent-status}${US}#{@agent-task}${US}#{pane_title}"
  local rows; rows="$(tmux list-panes -a -F "$fmt" 2>/dev/null || true)"

  if [ "$json" -eq 1 ]; then
    printf '['; local sep=""
    while IFS="$US" read -r cmd target pid role model attitude status task title; do
      [[ "$cmd" =~ $WORKER_CMD_RE ]] || continue
      printf '%s{"target":"%s","pid":"%s","role":"%s","model":"%s","attitude":"%s","status":"%s","task":"%s","title":"%s"}' \
        "$sep" "$target" "$pid" "$role" "$model" "$attitude" "$status" "$task" "${title//\"/\'}"
      sep=","
    done <<<"$rows"
    printf ']\n'
  else
    printf '%-26s %-12s %-8s %-9s %-9s %s\n' TARGET ROLE MODEL ATTITUDE STATUS TITLE
    while IFS="$US" read -r cmd target pid role model attitude status task title; do
      [[ "$cmd" =~ $WORKER_CMD_RE ]] || continue
      printf '%-26s %-12s %-8s %-9s %-9s %s\n' \
        "$target" "${role:--}" "${model:--}" "${attitude:--}" "${status:--}" "$title"
    done <<<"$rows"
  fi
}

# ── tag ──────────────────────────────────────────────────────────────────────
cmd_tag() {
  [ $# -ge 2 ] || die "usage: tag <target> k=v ..."
  local target="$1"; shift
  local kv key val
  for kv in "$@"; do
    key="${kv%%=*}"; val="${kv#*=}"
    case "$key" in
      role|model|attitude|effort|permission|budget|status|task|managed)
        tmux set-option -p -t "$target" "@agent-$key" "$val" ;;
      *) err "무시된 태그 키: $key" ;;
    esac
  done
}

# ── read ─────────────────────────────────────────────────────────────────────
cmd_read() {
  [ $# -ge 1 ] || die "usage: read <target> [lines]"
  local target="$1"; local lines="${2:-}"
  if [ -n "$lines" ]; then
    tmux capture-pane -p -t "$target" -S "-$lines"
  else
    tmux capture-pane -p -t "$target"
  fi
}

# ── ready (유휴 판정) ─────────────────────────────────────────────────────────
cmd_ready() {
  [ $# -ge 1 ] || die "usage: ready <target>"
  local screen; screen="$(tmux capture-pane -p -t "$1" 2>/dev/null || true)"
  if grep -qiE "$SPINNER_RE" <<<"$screen"; then return 1; fi   # busy
  if grep -qE "$PROMPT_RE" <<<"$screen"; then return 0; fi     # 프롬프트 존재 → ready
  return 1
}

# ── send (원자적 주입) ────────────────────────────────────────────────────────
cmd_send() {
  [ $# -ge 2 ] || die "usage: send <target> <file>"
  local target="$1" file="$2"
  [ -f "$file" ] || die "파일 없음: $file"
  local buf="tmuxctl-$$"
  tmux load-buffer -b "$buf" "$file"
  tmux paste-buffer -d -p -b "$buf" -t "$target"
  tmux send-keys -t "$target" Enter
}

# ── wait (마커 폴링) ──────────────────────────────────────────────────────────
cmd_wait() {
  [ $# -ge 2 ] || die "usage: wait <target> <marker> [timeout]"
  local target="$1" marker="$2" timeout="${3:-600}"
  local waited=0 screen
  while :; do
    screen="$(tmux capture-pane -p -t "$target" -S -200 2>/dev/null || true)"
    if grep -qF "[$marker BLOCKED" <<<"$screen"; then return 2; fi
    if grep -qF "[$marker DONE]" <<<"$screen"; then return 0; fi
    [ "$waited" -ge "$timeout" ] && return 1
    sleep "$POLL_INTERVAL"; waited=$((waited + POLL_INTERVAL))
  done
}

# ── apply-profile (기존 pane 부분 적용) ──────────────────────────────────────
cmd_apply_profile() {
  [ $# -ge 2 ] || die "usage: apply-profile <target> <preset|k=v ...>"
  local target="$1"; shift
  parse_profile "$@"
  # 태깅(의도 기록)
  local tags=()
  [ -n "$PF_MODEL" ] && tags+=("model=$PF_MODEL")
  [ -n "$PF_EFFORT" ] && tags+=("effort=$PF_EFFORT")
  [ -n "$PF_PERMISSION" ] && tags+=("permission=$PF_PERMISSION")
  [ -n "$PF_BUDGET" ] && tags+=("budget=$PF_BUDGET")
  [ -n "$PF_ATTITUDE" ] && tags+=("attitude=$PF_ATTITUDE")
  [ ${#tags[@]} -gt 0 ] && cmd_tag "$target" "${tags[@]}"
  # 런타임 적용: model, fast 는 슬래시 커맨드로 주입 가능
  if [ -n "$PF_MODEL" ]; then
    tmux send-keys -t "$target" "/model $PF_MODEL" Enter
  fi
  if [ "$PF_FAST" = "on" ]; then
    tmux send-keys -t "$target" "/fast" Enter
  fi
  # effort/permission/budget 은 런타임 변경 불가 → 경고
  if [ -n "$PF_EFFORT" ] || [ -n "$PF_PERMISSION" ] || [ -n "$PF_BUDGET" ]; then
    err "경고: effort/permission/budget 은 기존 pane 에 런타임 적용 불가(런치 시 고정). spawn 사용 시 강제됨. target=$target"
  fi
}

# ── spawn (프로파일대로 신규 pane 생성) ──────────────────────────────────────
cmd_spawn() {
  [ $# -ge 3 ] || die "usage: spawn <session> <count> <preset|k=v ...>"
  local session="$1" count="$2"; shift 2
  parse_profile "$@"
  [ -n "$PF_MODEL" ] || PF_MODEL="sonnet"
  local flags="--model $PF_MODEL"
  [ -n "$PF_EFFORT" ] && flags="$flags --effort $PF_EFFORT"
  [ -n "$PF_PERMISSION" ] && flags="$flags --permission-mode $PF_PERMISSION"
  [ -n "$PF_BUDGET" ] && flags="$flags --max-budget-usd $PF_BUDGET"
  # 기동 명령 — 기본 claude. 테스트/래퍼 용도로 env 오버라이드 가능.
  local launcher="${TMUXCTL_SPAWN_CMD:-claude}"
  local i target
  for ((i = 1; i <= count; i++)); do
    target="$(tmux split-window -t "$session" -P -F '#{session_name}:#{window_index}.#{pane_index}' "$launcher $flags")"
    tmux set-option -p -t "$target" @agent-managed 1
    [ -n "$PF_ATTITUDE" ] && tmux set-option -p -t "$target" @agent-attitude "$PF_ATTITUDE"
    tmux set-option -p -t "$target" @agent-model "$PF_MODEL"
    [ -n "$PF_EFFORT" ] && tmux set-option -p -t "$target" @agent-effort "$PF_EFFORT"
    tmux set-option -p -t "$target" @agent-status idle
    tmux select-layout -t "$session" tiled >/dev/null 2>&1 || true
    echo "$target"
  done
}

# ── dispatch ─────────────────────────────────────────────────────────────────
main() {
  require_tmux
  [ $# -ge 1 ] || die "usage: tmuxctl <discover|tag|read|ready|send|wait|apply-profile|spawn|preset> ..."
  local sub="$1"; shift
  case "$sub" in
    discover)       cmd_discover "$@" ;;
    tag)            cmd_tag "$@" ;;
    read)           cmd_read "$@" ;;
    ready)          cmd_ready "$@" ;;
    send)           cmd_send "$@" ;;
    wait)           cmd_wait "$@" ;;
    apply-profile)  cmd_apply_profile "$@" ;;
    spawn)          cmd_spawn "$@" ;;
    preset)         cmd_preset "$@" ;;
    *)              die "알 수 없는 서브커맨드: $sub" ;;
  esac
}

main "$@"
