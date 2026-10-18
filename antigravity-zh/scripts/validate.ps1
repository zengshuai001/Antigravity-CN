<#
.SYNOPSIS
    验证翻译文件的完整性。
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== 翻译完整性验证 ===" -ForegroundColor Cyan

$errors = 0
$warnings = 0

# 1. 检查翻译文件存在
$transFile = Join-Path $ProjectRoot "translations\nls.messages.zh-CN.json"
if (-not (Test-Path $transFile)) {
    Write-Error "翻译文件不存在: $transFile"
    exit 1
}

# 2. 检查原始文件
$origFile = Join-Path $ProjectRoot "source\nls.messages.original.json"
if (-not (Test-Path $origFile)) {
    Write-Warning "原始文件不存在，跳过对比验证"
    $warnings++
} else {
    $original = Get-Content $origFile -Raw -Encoding UTF8 | ConvertFrom-Json
    $translated = Get-Content $transFile -Raw -Encoding UTF8 | ConvertFrom-Json

    # 检查数量匹配
    if ($original.Count -ne $translated.Count) {
        Write-Host "[FAIL] 数量不匹配: 原始=$($original.Count), 翻译=$($translated.Count)" -ForegroundColor Red
        $errors++
    } else {
        Write-Host "[PASS] 消息数量匹配: $($translated.Count)" -ForegroundColor Green
    }

    # 检查空值
    $emptyCount = 0
    $untranslatedCount = 0
    for ($i = 0; $i -lt $translated.Count; $i++) {
        if ([string]::IsNullOrWhiteSpace($translated[$i])) {
            $emptyCount++
        } elseif ($translated[$i] -eq $original[$i]) {
            $untranslatedCount++
        }
    }

    $translatedCount = $translated.Count - $emptyCount - $untranslatedCount
    $pct = [math]::Round($translatedCount / $translated.Count * 100, 1)

    Write-Host "  已翻译: $translatedCount ($pct%)" -ForegroundColor $(if ($pct -gt 80) { "Green" } elseif ($pct -gt 50) { "Yellow" } else { "Red" })
    Write-Host "  未翻译: $untranslatedCount" -ForegroundColor Yellow
    Write-Host "  空值: $emptyCount" -ForegroundColor $(if ($emptyCount -gt 0) { "Red" } else { "Green" })

    if ($emptyCount -gt 0) {
        Write-Host "[WARN] 存在 $emptyCount 个空值" -ForegroundColor Yellow
        $warnings++
    }

    # 检查占位符完整性
    Write-Host "`n检查占位符完整性..." -ForegroundColor Yellow
    $placeholderErrors = 0
    for ($i = 0; $i -lt [Math]::Min($original.Count, $translated.Count); $i++) {
        $origPlaceholders = [regex]::Matches($original[$i], '\{(\d+)\}') | ForEach-Object { $_.Value } | Sort-Object
        $transPlaceholders = [regex]::Matches($translated[$i], '\{(\d+)\}') | ForEach-Object { $_.Value } | Sort-Object

        $origStr = ($origPlaceholders -join ",")
        $transStr = ($transPlaceholders -join ",")

        if ($origStr -ne $transStr) {
            $placeholderErrors++
            if ($placeholderErrors -le 5) {
                Write-Host "  [$i] 占位符不匹配: 原始=[$origStr] 翻译=[$transStr]" -ForegroundColor Red
            }
        }
    }
    if ($placeholderErrors -gt 0) {
        Write-Host "[FAIL] $placeholderErrors 处占位符不匹配" -ForegroundColor Red
        $errors++
    } else {
        Write-Host "[PASS] 占位符完整性检查通过" -ForegroundColor Green
    }
}

# 结果汇总
Write-Host "`n=== 验证结果 ===" -ForegroundColor Cyan
if ($errors -eq 0) {
    Write-Host "通过! ($warnings 个警告)" -ForegroundColor Green
} else {
    Write-Host "失败! $errors 个错误, $warnings 个警告" -ForegroundColor Red
    exit 1
}
