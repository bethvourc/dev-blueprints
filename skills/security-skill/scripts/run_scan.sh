#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH="${1:-.}"
OUTPUT_DIR="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RG_EXCLUDES=(
  -g '!**/.git/**'
  -g '!**/node_modules/**'
  -g '!**/.next/**'
  -g '!**/dist/**'
  -g '!**/build/**'
  -g '!**/coverage/**'
  -g '!**/target/**'
  -g '!**/.turbo/**'
)

RG_CODE_GLOBS=(
  -g '*.js' -g '*.jsx' -g '*.mjs' -g '*.cjs'
  -g '*.ts' -g '*.tsx'
  -g '*.py' -g '*.rb' -g '*.php'
  -g '*.go' -g '*.rs' -g '*.java' -g '*.kt' -g '*.cs'
  -g '*.sh' -g '*.bash' -g '*.zsh'
  -g '*.json' -g '*.yaml' -g '*.yml' -g '*.toml' -g '*.ini' -g '*.conf'
  -g '*.sql' -g '*.graphql' -g '*.gql'
  -g '*.env' -g '*.env.*'
  -g '*.tf'
  -g 'Dockerfile'
)

if [[ ! -d "$TARGET_PATH" ]]; then
  echo "[security-scan] error: target path is not a directory: $TARGET_PATH" >&2
  exit 2
fi

TARGET_PATH="$(cd "$TARGET_PATH" && pwd)"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"

if [[ -z "$OUTPUT_DIR" ]]; then
  OUTPUT_DIR="/tmp/security-scan-${TIMESTAMP}"
fi

mkdir -p "$OUTPUT_DIR/raw" "$OUTPUT_DIR/meta" "$OUTPUT_DIR/findings"

echo "[security-scan] target: $TARGET_PATH"
echo "[security-scan] output: $OUTPUT_DIR"

record_status() {
  local name="$1"
  local code="$2"
  printf '%s\n' "$code" > "$OUTPUT_DIR/meta/${name}.status"
}

run_in_dir() {
  local name="$1"
  local dir="$2"
  shift 2
  local out="$OUTPUT_DIR/raw/${name}.log"
  local code=0

  set +e
  (
    cd "$dir"
    "$@"
  ) >"$out" 2>&1
  code=$?
  set -e

  record_status "$name" "$code"
}

find_named_files() {
  local filename="$1"
  find "$TARGET_PATH" \
    \( -type d \( -name .git -o -name node_modules -o -name .next -o -name dist -o -name build -o -name target -o -name .turbo -o -name coverage -o -name .venv -o -name venv \) -prune \) -o \
    \( -type f -name "$filename" -print \)
}

find_first_manifest() {
  local filename="$1"
  find_named_files "$filename" | head -n 1 || true
}

filter_internal_hits() {
  local result_file="$1"
  local tmp_file="${result_file}.tmp"

  if [[ ! -s "$result_file" ]]; then
    return
  fi

  grep -Fv "${SKILL_ROOT}/" "$result_file" > "$tmp_file" || true
  mv "$tmp_file" "$result_file"
}

cat > "$OUTPUT_DIR/meta/scan_context.json" <<JSON
{
  "timestamp_utc": "${TIMESTAMP}",
  "target_path": "${TARGET_PATH}",
  "output_dir": "${OUTPUT_DIR}"
}
JSON

if command -v rg >/dev/null 2>&1; then
  rg --files --hidden "${RG_EXCLUDES[@]}" "$TARGET_PATH" > "$OUTPUT_DIR/raw/file_inventory.txt" || true
else
  find "$TARGET_PATH" \
    \( -type d \( -name .git -o -name node_modules -o -name .next -o -name dist -o -name build -o -name target -o -name coverage \) -prune \) -o \
    \( -type f -print \) > "$OUTPUT_DIR/raw/file_inventory.txt"
fi

find "$TARGET_PATH" \
  \( -type d \( -name .git -o -name node_modules -o -name .next -o -name dist -o -name build -o -name target -o -name .turbo -o -name coverage -o -name .venv -o -name venv \) -prune \) -o \
  \( -type f \( -name 'package.json' -o -name 'pnpm-lock.yaml' -o -name 'package-lock.json' -o -name 'yarn.lock' -o -name 'requirements.txt' -o -name 'pyproject.toml' -o -name 'Pipfile.lock' -o -name 'Cargo.toml' -o -name 'Cargo.lock' -o -name 'go.mod' -o -name '.env' -o -name '.env.*' \) -print \) \
  > "$OUTPUT_DIR/raw/manifest_inventory.txt" || true

cat > "$OUTPUT_DIR/meta/patterns.tsv" <<'PATTERNS'
id	category	severity	title	regex
command_exec	Injection vulnerabilities	HIGH	Command execution sink present	(^|[^A-Za-z0-9_.])(execFileSync|execFile|execSync|spawnSync|spawn|system|popen|exec)\s*\(
eval_usage	Injection vulnerabilities	HIGH	Dynamic eval usage	\beval\s*\(
new_function	Injection vulnerabilities	HIGH	Dynamic Function constructor usage	\bnew\s+Function\s*\(
path_traversal	Injection vulnerabilities	MEDIUM	Path construction from request input	(path\.join|path\.resolve|fs\.(readFile|readFileSync|createReadStream|writeFile|writeFileSync))[^\n]*(req\.|params\.|query\.|body\.)
unsafe_html	Injection vulnerabilities	MEDIUM	Potential unescaped HTML rendering	(dangerouslySetInnerHTML|innerHTML\s*=)
jwt_none	Authentication & Authorization	HIGH	JWT alg none detected	alg\s*[:=]\s*["']none["']
weak_hash	Cryptography	MEDIUM	Weak hash function usage	\b(md5|sha1)\s*\(
insecure_random	Cryptography	LOW	Math.random usage in potentially security-sensitive logic	Math\.random\s*\(
csrf_disabled	Authentication & Authorization	MEDIUM	Potential CSRF protection disablement	(csrf\s*[:=]\s*false|ignoreMethods\s*:\s*\[\])
open_redirect	Configuration & Infrastructure	MEDIUM	Potential open redirect sink	(res\.redirect|redirect\()\s*\(?.*(req\.|query\.|params\.)
cors_wildcard	Configuration & Infrastructure	MEDIUM	Wildcard CORS with credentials risk	(origin\s*:\s*["']\*["']|Access-Control-Allow-Origin\s*[:=]\s*["']\*["'])
debug_prod	Configuration & Infrastructure	LOW	Debug or development mode toggle present	(NODE_ENV\s*!==?\s*["']production["']|debug\s*[:=]\s*true)
PATTERNS

cat > "$OUTPUT_DIR/meta/secret_patterns.tsv" <<'SECRETS'
id	category	severity	title	regex
aws_access_key	Secrets & Credential Exposure	CRITICAL	Possible AWS access key	AKIA[0-9A-Z]{16}
github_token	Secrets & Credential Exposure	HIGH	Possible GitHub token	gh[pousr]_[A-Za-z0-9_]{20,}
openai_key	Secrets & Credential Exposure	HIGH	Possible OpenAI API key	sk-[A-Za-z0-9]{20,}
private_key_block	Secrets & Credential Exposure	CRITICAL	Private key block detected	-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
generic_password_assign	Secrets & Credential Exposure	MEDIUM	Possible hardcoded password assignment	(password|passwd|pwd)\s*[:=]\s*["'][^"']{6,}["']
slack_token	Secrets & Credential Exposure	HIGH	Possible Slack token	xox[baprs]-[A-Za-z0-9-]{10,}
SECRETS

echo -e "id\thits" > "$OUTPUT_DIR/meta/pattern_hit_counts.tsv"
while IFS=$'\t' read -r id _category _severity _title regex; do
  if [[ "$id" == "id" ]]; then
    continue
  fi

  out="$OUTPUT_DIR/raw/pattern_${id}.txt"
  if command -v rg >/dev/null 2>&1; then
    rg -n --no-heading --hidden "${RG_EXCLUDES[@]}" "${RG_CODE_GLOBS[@]}" -e "$regex" "$TARGET_PATH" > "$out" || true
  else
    grep -RInE --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist --exclude-dir=build "$regex" "$TARGET_PATH" > "$out" || true
  fi

  filter_internal_hits "$out"

  hits="$(wc -l < "$out" | tr -d ' ')"
  echo -e "${id}\t${hits}" >> "$OUTPUT_DIR/meta/pattern_hit_counts.tsv"
done < "$OUTPUT_DIR/meta/patterns.tsv"

echo -e "id\thits" > "$OUTPUT_DIR/meta/secret_hit_counts.tsv"
while IFS=$'\t' read -r id _category _severity _title regex; do
  if [[ "$id" == "id" ]]; then
    continue
  fi

  out="$OUTPUT_DIR/raw/secret_${id}.txt"
  if command -v rg >/dev/null 2>&1; then
    rg -n --no-heading --hidden "${RG_EXCLUDES[@]}" -e "$regex" "$TARGET_PATH" > "$out" || true
  else
    grep -RInE --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist --exclude-dir=build "$regex" "$TARGET_PATH" > "$out" || true
  fi

  filter_internal_hits "$out"

  hits="$(wc -l < "$out" | tr -d ' ')"
  echo -e "${id}\t${hits}" >> "$OUTPUT_DIR/meta/secret_hit_counts.tsv"
done < "$OUTPUT_DIR/meta/secret_patterns.tsv"

PNPM_LOCK="$(find_first_manifest pnpm-lock.yaml)"
if [[ -n "$PNPM_LOCK" && -x "$(command -v pnpm || true)" ]]; then
  run_in_dir "deps_pnpm_audit" "$(dirname "$PNPM_LOCK")" env npm_config_fetch_retries=0 npm_config_fetch_timeout=5000 pnpm audit --prod --json
else
  record_status "deps_pnpm_audit" "127"
fi

NPM_LOCK="$(find_first_manifest package-lock.json)"
if [[ -n "$NPM_LOCK" && -x "$(command -v npm || true)" ]]; then
  run_in_dir "deps_npm_audit" "$(dirname "$NPM_LOCK")" env npm_config_fetch_retries=0 npm_config_fetch_timeout=5000 npm audit --omit=dev --json
else
  record_status "deps_npm_audit" "127"
fi

REQ_TXT="$(find_first_manifest requirements.txt)"
if [[ -n "$REQ_TXT" && -x "$(command -v pip-audit || true)" ]]; then
  run_in_dir "deps_pip_audit" "$(dirname "$REQ_TXT")" pip-audit -f json
else
  record_status "deps_pip_audit" "127"
fi

CARGO_LOCK="$(find_first_manifest Cargo.lock)"
if [[ -n "$CARGO_LOCK" && -x "$(command -v cargo-audit || true)" ]]; then
  run_in_dir "deps_cargo_audit" "$(dirname "$CARGO_LOCK")" cargo audit --json
else
  record_status "deps_cargo_audit" "127"
fi

if [[ -x "$(command -v python3 || true)" ]]; then
  set +e
  python3 "$SCRIPT_DIR/collect_findings.py" \
    --scan-dir "$OUTPUT_DIR" \
    --output-json "$OUTPUT_DIR/findings/findings.json" \
    --output-markdown "$OUTPUT_DIR/findings/findings.md" \
    --template "$SCRIPT_DIR/../references/report_template.md"
  code=$?
  set -e
  record_status "collect_findings" "$code"
else
  record_status "collect_findings" "127"
fi

echo "[security-scan] complete"
echo "[security-scan] findings json: $OUTPUT_DIR/findings/findings.json"
echo "[security-scan] findings markdown: $OUTPUT_DIR/findings/findings.md"
echo "[security-scan] raw artifacts: $OUTPUT_DIR/raw"
echo "[security-scan] metadata: $OUTPUT_DIR/meta"
