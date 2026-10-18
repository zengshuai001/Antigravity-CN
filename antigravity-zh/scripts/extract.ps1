<#
.SYNOPSIS
    从 Antigravity 2.0 提取原始英文文本用于翻译。

.DESCRIPTION
    提取 NLS 消息、扩展翻译文本和 jetskiAgent 硬编码字符串。
#>
[CmdletBinding()]
param(
    [switch]$Update,
    [string]$AntigravityPath = "$env:LOCALAPPDATA\Programs\Antigravity"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourceDir = Join-Path $ProjectRoot "source"

Write-Host "=== Antigravity 2.0 文本提取工具 ===" -ForegroundColor Cyan

# 检测安装
if (-not (Test-Path "$AntigravityPath\Antigravity.exe")) {
    Write-Error "未找到 Antigravity: $AntigravityPath"
    exit 1
}

# 读取版本信息
$productJson = Get-Content "$AntigravityPath\resources\app\product.json" -Raw | ConvertFrom-Json
$exeVersion = $null
$exePath = Join-Path $AntigravityPath "Antigravity.exe"
if (Test-Path $exePath) {
    $exeVersion = (Get-Item $exePath).VersionInfo.FileVersion
}
Write-Host "检测到版本: $($productJson.nameShort) App=$exeVersion IDE=$($productJson.ideVersion)" -ForegroundColor Green

$previousMessagesPath = Join-Path $SourceDir "nls.messages.original.json"
$previousMessages = $null
if ($Update -and (Test-Path $previousMessagesPath)) {
    $previousMessages = Get-Content $previousMessagesPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

# 创建输出目录
New-Item -Path $SourceDir -ItemType Directory -Force | Out-Null
New-Item -Path "$SourceDir\extensions" -ItemType Directory -Force | Out-Null

# 1. 提取 NLS 文件
Write-Host "`n[1/4] 提取 NLS 消息文件..." -ForegroundColor Yellow
$nlsDir = "$AntigravityPath\resources\app\out"

Copy-Item "$nlsDir\nls.messages.json" "$SourceDir\nls.messages.original.json" -Force
Copy-Item "$nlsDir\nls.keys.json" "$SourceDir\nls.keys.original.json" -Force

$messages = Get-Content "$SourceDir\nls.messages.original.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$keys = Get-Content "$SourceDir\nls.keys.original.json" -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "  消息总数: $($messages.Count)" -ForegroundColor White
Write-Host "  键组总数: $($keys.Count)" -ForegroundColor White

# 2. 分析消息分类
Write-Host "`n[2/4] 分析消息分类..." -ForegroundColor Yellow
$categories = @{}
$index = 0
foreach ($keyGroup in $keys) {
    $modulePath = $keyGroup[0]
    $keyNames = $keyGroup[1..$($keyGroup.Count - 1)]
    $count = $keyNames.Count

    # 提取顶级模块名
    $parts = $modulePath -split "/"
    if ($parts.Count -ge 2) {
        $category = "$($parts[0])/$($parts[1])"
    } else {
        $category = $modulePath
    }

    if (-not $categories.ContainsKey($category)) {
        $categories[$category] = @{ count = 0; startIndex = $index; modules = @() }
    }
    $categories[$category].count += $count
    $categories[$category].endIndex = $index + $count - 1
    $categories[$category].modules += $modulePath

    $index += $count
}

# 输出分析结果
$analysis = @{
    totalMessages = $messages.Count
    totalKeyGroups = $keys.Count
    extractDate = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
    categories = @{}
}
foreach ($cat in ($categories.Keys | Sort-Object)) {
    $analysis.categories[$cat] = @{
        count = $categories[$cat].count
        startIndex = $categories[$cat].startIndex
        endIndex = $categories[$cat].endIndex
        moduleCount = $categories[$cat].modules.Count
    }
    $pct = [math]::Round($categories[$cat].count / $messages.Count * 100, 1)
    Write-Host "  $cat : $($categories[$cat].count) 条 ($pct%)" -ForegroundColor White
}

$analysis | ConvertTo-Json -Depth 5 | Out-File "$SourceDir\analysis.json" -Encoding UTF8
Write-Host "  分析结果已保存: source/analysis.json" -ForegroundColor Green

# 3. 提取扩展翻译
Write-Host "`n[3/4] 提取扩展翻译文件..." -ForegroundColor Yellow
$extDir = "$AntigravityPath\resources\app\extensions"
$agyExtensions = @(
    "antigravity",
    "antigravity-code-executor",
    "antigravity-dev-containers",
    "antigravity-remote-openssh",
    "antigravity-remote-wsl"
)

foreach ($ext in $agyExtensions) {
    $extPath = Join-Path $extDir $ext
    if (Test-Path $extPath) {
        $outDir = Join-Path "$SourceDir\extensions" $ext
        New-Item -Path $outDir -ItemType Directory -Force | Out-Null

        # 复制 package.json 和 package.nls*.json
        Get-ChildItem $extPath -Filter "package*.json" | ForEach-Object {
            Copy-Item $_.FullName (Join-Path $outDir $_.Name) -Force
            Write-Host "  $ext/$($_.Name)" -ForegroundColor White
        }

        # 复制 l10n 目录
        $l10nDir = Join-Path $extPath "l10n"
        if (Test-Path $l10nDir) {
            Copy-Item $l10nDir (Join-Path $outDir "l10n") -Recurse -Force
            Write-Host "  $ext/l10n/ (已复制)" -ForegroundColor White
        }
    } else {
        Write-Host "  $ext (未找到)" -ForegroundColor DarkGray
    }
}

# 4. 提取 jetskiAgent 字符串样本
Write-Host "`n[4/4] 采样 jetskiAgent 字符串..." -ForegroundColor Yellow
$jetskiJs = "$AntigravityPath\resources\app\out\jetskiAgent\main.js"
if (Test-Path $jetskiJs) {
    # 提取看起来像用户界面文本的字符串
    $content = Get-Content $jetskiJs -Raw -Encoding UTF8
    $matches = [regex]::Matches($content, '(?<=")((?:[A-Z][a-z]+ ){1,6}[a-zA-Z]+)(?=")')
    $uniqueStrings = $matches | ForEach-Object { $_.Groups[1].Value } |
        Where-Object { $_.Length -gt 5 -and $_.Length -lt 100 } |
        Sort-Object -Unique |
        Select-Object -First 200

    $uniqueStrings | Out-File "$SourceDir\jetski-strings-sample.txt" -Encoding UTF8
    Write-Host "  找到 $($uniqueStrings.Count) 个候选UI字符串" -ForegroundColor White
    Write-Host "  样本已保存: source/jetski-strings-sample.txt" -ForegroundColor Green
}

Write-Host "`n=== 提取完成 ===" -ForegroundColor Cyan
Write-Host "总消息数: $($messages.Count)" -ForegroundColor Green
Write-Host "下一步: 运行翻译生成脚本" -ForegroundColor Yellow

if ($Update) {
    Write-Host "`n[Update] 生成版本更新报告..." -ForegroundColor Yellow
    $reportDir = Join-Path $ProjectRoot "releases"
    New-Item -Path $reportDir -ItemType Directory -Force | Out-Null

    $changedSameIndex = 0
    if ($previousMessages) {
        $sharedCount = [Math]::Min($previousMessages.Count, $messages.Count)
        for ($i = 0; $i -lt $sharedCount; $i++) {
            if ($previousMessages[$i] -ne $messages[$i]) {
                $changedSameIndex++
            }
        }
    }

    $uiMainSource = $env:AGY_UI_MAIN_SOURCE
    $uiMainHash = $null
    if ($uiMainSource -and (Test-Path $uiMainSource)) {
        $uiMainHash = (Get-FileHash -Algorithm SHA256 -Path $uiMainSource).Hash.ToUpperInvariant()
    }

    $report = @{
        generatedAt = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
        antigravityVersion = $exeVersion
        ideVersion = $productJson.ideVersion
        internalVersion = if (Test-Path "$AntigravityPath\resources\app\package.json") {
            (Get-Content "$AntigravityPath\resources\app\package.json" -Raw | ConvertFrom-Json).version
        } else {
            $null
        }
        appAsarSha256 = if (Test-Path "$AntigravityPath\resources\app.asar") {
            (Get-FileHash -Algorithm SHA256 -Path "$AntigravityPath\resources\app.asar").Hash.ToUpperInvariant()
        } else {
            $null
        }
        nlsMessagesSha256 = (Get-FileHash -Algorithm SHA256 -Path "$SourceDir\nls.messages.original.json").Hash.ToUpperInvariant()
        uiMainSource = $uiMainSource
        uiMainSha256 = $uiMainHash
        previousMessageCount = if ($previousMessages) { $previousMessages.Count } else { $null }
        currentMessageCount = $messages.Count
        addedByIndex = if ($previousMessages) { [Math]::Max(0, $messages.Count - $previousMessages.Count) } else { $null }
        removedByIndex = if ($previousMessages) { [Math]::Max(0, $previousMessages.Count - $messages.Count) } else { $null }
        changedAtSameIndex = if ($previousMessages) { $changedSameIndex } else { $null }
        recommendation = "Core translations may be updated after validate.ps1 passes. Enable AI UI only after adding a matching uiMainSha256 to patches/ai-ui-compat.json."
    }

    $reportPath = Join-Path $reportDir "version-update-report.json"
    $report | ConvertTo-Json -Depth 5 | Out-File $reportPath -Encoding UTF8
    Write-Host "  报告已保存: releases/version-update-report.json" -ForegroundColor Green
}
