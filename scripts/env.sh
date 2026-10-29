export HOME="/Users/dy.chen"
export PATH="/Users/dy.chen/.local/bin:$PATH"
export PROJECT_DIR="/Users/dy.chen/Personal/stock"
export PWD="$PROJECT_DIR"
export LOG_DIR="$PROJECT_DIR/logs"
# token 存放在未提交的本地文件（已 gitignore），不要写进本文件
if [ -r "$PROJECT_DIR/scripts/.claude_oauth_token" ]; then
  CLAUDE_CODE_OAUTH_TOKEN="$(cat "$PROJECT_DIR/scripts/.claude_oauth_token")"
  export CLAUDE_CODE_OAUTH_TOKEN
fi
#export NO_PROXY="localhost,127.0.0.1,https://open.feishu.cn"