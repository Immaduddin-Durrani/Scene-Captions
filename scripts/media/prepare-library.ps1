param(
    [ValidateSet('sintel', 'tears-of-steel', 'all')]
    [string]$Film = 'all'
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$cache = Join-Path $root '.media-cache/library'
$media = Join-Path $root 'public/media'
foreach ($tool in @('curl.exe', 'ffmpeg', 'ffprobe')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "Install $tool before running this script." }
}
New-Item -ItemType Directory -Force -Path $cache, $media | Out-Null

function Get-Resource([string]$Url, [string]$Path, [long]$ExpectedBytes = 0) {
    if (Test-Path -LiteralPath $Path) {
        if ($ExpectedBytes -gt 0 -and (Get-Item -LiteralPath $Path).Length -ne $ExpectedBytes) {
            throw "Cached file has an unexpected size: $Path. Rename it and try again."
        }
        return
    }
    Write-Host "Downloading $Url"
    $partial = "$Path.partial"
    & curl.exe --fail --location --retry 3 --connect-timeout 30 --output $partial -- $Url
    if ($LASTEXITCODE -ne 0) { throw "Download failed; incomplete file remains at $partial" }
    if ($ExpectedBytes -gt 0 -and (Get-Item -LiteralPath $partial).Length -ne $ExpectedBytes) {
        throw "Download size differs from the checked source: $partial"
    }
    Move-Item -LiteralPath $partial -Destination $Path
}

function Read-Probe([string]$Path) {
    $result = & ffprobe -v error -show_format -show_streams -of json $Path
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect media: $Path" }
    return ($result | Out-String | ConvertFrom-Json)
}

function Test-BrowserCopy([string]$Path, $Source) {
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    try { $probe = Read-Probe $Path } catch { return $false }
    $sourceVideo = @($Source.streams | Where-Object codec_type -eq 'video')[0]
    $videos = @($probe.streams | Where-Object codec_type -eq 'video')
    $audio = @($probe.streams | Where-Object codec_type -eq 'audio')
    $sourceSeconds = [double]::Parse([string]$Source.format.duration, [Globalization.CultureInfo]::InvariantCulture)
    $seconds = [double]::Parse([string]$probe.format.duration, [Globalization.CultureInfo]::InvariantCulture)
    return ($videos.Count -eq 1 -and $videos[0].width -eq $sourceVideo.width -and
        $videos[0].height -eq $sourceVideo.height -and $videos[0].codec_name -eq 'h264' -and
        $audio.Count -eq 1 -and $audio[0].codec_name -eq 'aac' -and
        [Math]::Abs($seconds - $sourceSeconds) -le 1)
}

$titles = @(
    @{ Id = 'sintel'; Title = 'Sintel'; Url = 'https://download.blender.org/durian/movies/Sintel.2010.720p.mkv.zip'; Bytes = 681285470; Extension = 'zip'; Credit = '(c) 2010 Blender Foundation / durian.blender.org'; About = 'https://durian.blender.org/about/' },
    @{ Id = 'tears-of-steel'; Title = 'Tears of Steel'; Url = 'https://download.blender.org/demo/movies/ToS/tears_of_steel_720p.mov'; Bytes = 372178639; Extension = 'mov'; Credit = '(c) 2012 Blender Foundation / mango.blender.org'; About = 'https://mango.blender.org/about/' }
)
foreach ($title in $titles) {
    if ($Film -ne 'all' -and $Film -ne $title.Id) { continue }
    $download = Join-Path $cache "$($title.Id).$($title.Extension)"
    Get-Resource $title.Url $download $title.Bytes
    $inputFile = $download
    if ($title.Extension -eq 'zip') {
        $inputFile = Join-Path $cache 'sintel-source.mkv'
        if (-not (Test-Path -LiteralPath $inputFile)) {
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            $archive = [IO.Compression.ZipFile]::OpenRead($download)
            try {
                $entries = @($archive.Entries | Where-Object { $_.FullName.EndsWith('.mkv', [StringComparison]::OrdinalIgnoreCase) })
                if ($entries.Count -ne 1) { throw 'Expected one MKV movie in the Sintel archive.' }
                $stream = $entries[0].Open()
                try {
                    $target = [IO.File]::Create("$inputFile.partial")
                    try { $stream.CopyTo($target) } finally { $target.Dispose() }
                } finally { $stream.Dispose() }
                Move-Item -LiteralPath "$inputFile.partial" -Destination $inputFile
            } finally { $archive.Dispose() }
        }
    }
    $source = Read-Probe $inputFile
    $duration = [double]::Parse([string]$source.format.duration, [Globalization.CultureInfo]::InvariantCulture)
    if ($duration -le 0 -or $duration -gt 1800) { throw 'Movie must be valid and at most 30 minutes. Nothing will be trimmed.' }
    if (@($source.streams | Where-Object codec_type -eq 'audio').Count -eq 0) { throw 'The source has no audio track.' }
    $output = Join-Path $media "$($title.Id).mp4"
    $rebuilt = -not (Test-BrowserCopy $output $source)
    if ($rebuilt) {
        $staged = Join-Path $cache "$($title.Id)-browser.mp4"
        & ffmpeg -nostdin -y -v error -i $inputFile -map 0:v:0 -map 0:a:0 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -ac 2 -movflags +faststart $staged
        if ($LASTEXITCODE -ne 0) { throw 'Browser video conversion failed.' }
        if (-not (Test-BrowserCopy $staged $source)) { throw 'Converted video failed resolution, codec, audio or duration checks.' }
        Move-Item -LiteralPath $staged -Destination $output -Force
    }
    $verified = Read-Probe $output
    $outputDuration = [double]::Parse([string]$verified.format.duration, [Globalization.CultureInfo]::InvariantCulture)
    if ([Math]::Abs($outputDuration - $duration) -gt 1 -or @($verified.streams | Where-Object codec_type -eq 'audio').Count -eq 0) {
        throw "Output failed duration/audio checks: $output"
    }
    $poster = Join-Path $media "$($title.Id)-poster.jpg"
    if ($rebuilt -or -not (Test-Path -LiteralPath $poster)) {
        & ffmpeg -nostdin -y -v error -ss 60 -i $output -frames:v 1 -q:v 3 $poster
        if ($LASTEXITCODE -ne 0) { throw 'Poster extraction failed.' }
    }
    $vtt = Join-Path $media "$($title.Id)-en.vtt"
    $subtitleSource = $null
    if ($title.Id -eq 'tears-of-steel') {
        $srt = Join-Path $cache 'TOS-en.srt'
        $subtitleSource = 'https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt'
        Get-Resource $subtitleSource $srt
        if (-not (Test-Path -LiteralPath $vtt)) {
            & ffmpeg -nostdin -v error -i $srt $vtt
            if ($LASTEXITCODE -ne 0) { throw 'Subtitle conversion failed.' }
        }
    } else {
        $english = @($source.streams | Where-Object { $_.codec_type -eq 'subtitle' -and $_.tags.language -in @('eng', 'en') })
        if ($english.Count -gt 0) {
            $subtitleSource = 'English subtitle stream embedded in official Sintel MKV'
            if (-not (Test-Path -LiteralPath $vtt)) {
                & ffmpeg -nostdin -v error -i $inputFile -map "0:$($english[0].index)" -c:s webvtt $vtt
                if ($LASTEXITCODE -ne 0) { throw 'Embedded subtitle conversion failed.' }
            }
        } else { Write-Warning 'No tagged English subtitle stream found in Sintel. No subtitle has been guessed.' }
    }
    $subtitleReady = (Test-Path -LiteralPath $vtt) -and $null -ne $subtitleSource
    [ordered]@{
        id = $title.Id; title = $title.Title; durationSeconds = $outputDuration
        video = "/media/$($title.Id).mp4"; poster = "/media/$($title.Id)-poster.jpg"
        englishSubtitles = $(if ($subtitleReady) { "/media/$($title.Id)-en.vtt" } else { $null })
        subtitleSource = $subtitleSource; subtitleTimingReviewed = $false
        nonSpeechCaptionStatus = 'not-prepared'; source = $title.Url
        credit = $title.Credit; license = 'CC BY 3.0'; licenseSource = $title.About
        modifications = 'Original 720p-release dimensions retained, H.264 video, stereo AAC audio, extracted still; full duration and credits retained'
        sha256 = (Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash.ToLowerInvariant()
        bytes = (Get-Item -LiteralPath $output).Length
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $media "$($title.Id).resources.json") -Encoding UTF8
    Write-Host "Ready: $output (audio included). Sound-caption review is still required."
}
Write-Host 'Finished. Original downloads remain in .media-cache/library; no files were added to Git.'
