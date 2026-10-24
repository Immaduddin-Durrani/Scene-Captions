param(
    [Parameter(Mandatory=$true)][string]$ArchivePath,
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($ArchivePath)
try {
    $movies = @($archive.Entries | Where-Object { $_.FullName.EndsWith('.m4v', [StringComparison]::OrdinalIgnoreCase) })
    if ($movies.Count -ne 1) { throw 'Expected exactly one movie in the official archive.' }
    # Copy only the selected entry into the caller's explicit file, never ZIP paths.
    $source = $movies[0].Open()
    try {
        $destination = [System.IO.File]::Create($OutputPath)
        try { $source.CopyTo($destination) } finally { $destination.Dispose() }
    } finally { $source.Dispose() }
} finally { $archive.Dispose() }
