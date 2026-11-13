$ErrorActionPreference = 'Stop'
$ModelTestRoot = $PSScriptRoot
$ModelWorkspaceRoot = (Resolve-Path (Join-Path $ModelTestRoot '../../..')).Path
$env:UV_CACHE_DIR = Join-Path $ModelTestRoot 'cache/uv'
$env:HF_HOME = Join-Path $ModelTestRoot 'cache/huggingface'
$env:TORCH_HOME = Join-Path $ModelTestRoot 'cache/torch'
$env:XDG_CACHE_HOME = Join-Path $ModelTestRoot 'cache/xdg'
$env:TEMP = Join-Path $ModelTestRoot 'tmp'
$env:TMP = $env:TEMP
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$env:DO_NOT_TRACK = '1'
$env:HF_HUB_DISABLE_XET = '1'
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'
$env:TOKENIZERS_PARALLELISM = 'false'
$env:CUDA_VISIBLE_DEVICES = '0'
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:PYTHONUTF8 = '1'
$env:PYTHONUNBUFFERED = '1'
foreach ($ModelCachePath in @($env:UV_CACHE_DIR, $env:HF_HOME, $env:TORCH_HOME, $env:XDG_CACHE_HOME, $env:TEMP)) {
    New-Item -ItemType Directory -Path $ModelCachePath -Force | Out-Null
}
