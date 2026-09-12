param(
  [int]$Port = 8017
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Server = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
$Server.Start()

Write-Host "Serving $Root at http://localhost:$Port/website/index.html"
Write-Host "Press Ctrl+C to stop."

$MimeTypes = @{
  ".html" = "text/html; charset=utf-8"
  ".css" = "text/css; charset=utf-8"
  ".js" = "application/javascript; charset=utf-8"
  ".json" = "application/json; charset=utf-8"
  ".png" = "image/png"
  ".jpg" = "image/jpeg"
  ".jpeg" = "image/jpeg"
  ".txt" = "text/plain; charset=utf-8"
}

function Send-Response($Stream, [int]$StatusCode, [string]$Reason, [byte[]]$Body, [string]$ContentType) {
  $Header = "HTTP/1.1 $StatusCode $Reason`r`nContent-Type: $ContentType`r`nContent-Length: $($Body.Length)`r`nConnection: close`r`n`r`n"
  $HeaderBytes = [System.Text.Encoding]::ASCII.GetBytes($Header)
  $Stream.Write($HeaderBytes, 0, $HeaderBytes.Length)
  if ($Body.Length -gt 0) {
    $Stream.Write($Body, 0, $Body.Length)
  }
}

try {
  while ($true) {
    $Client = $Server.AcceptTcpClient()
    $Stream = $Client.GetStream()
    $Buffer = New-Object byte[] 4096
    $Read = $Stream.Read($Buffer, 0, $Buffer.Length)
    $Request = [System.Text.Encoding]::ASCII.GetString($Buffer, 0, $Read)
    $FirstLine = ($Request -split "`r?`n")[0]
    $Parts = $FirstLine -split " "

    if ($Parts.Length -lt 2) {
      Send-Response $Stream 400 "Bad Request" ([System.Text.Encoding]::UTF8.GetBytes("Bad Request")) "text/plain; charset=utf-8"
      $Client.Close()
      continue
    }

    $RequestPath = [Uri]::UnescapeDataString($Parts[1].Split("?")[0].TrimStart("/"))
    if ([string]::IsNullOrWhiteSpace($RequestPath)) {
      $RequestPath = "website/index.html"
    }

    $LocalPath = Join-Path $Root $RequestPath
    $ResolvedRoot = [System.IO.Path]::GetFullPath($Root)
    $ResolvedPath = [System.IO.Path]::GetFullPath($LocalPath)

    if (-not $ResolvedPath.StartsWith($ResolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
      Send-Response $Stream 403 "Forbidden" ([System.Text.Encoding]::UTF8.GetBytes("Forbidden")) "text/plain; charset=utf-8"
      $Client.Close()
      continue
    }

    if (-not [System.IO.File]::Exists($ResolvedPath)) {
      Send-Response $Stream 404 "Not Found" ([System.Text.Encoding]::UTF8.GetBytes("Not Found")) "text/plain; charset=utf-8"
      $Client.Close()
      continue
    }

    $Bytes = [System.IO.File]::ReadAllBytes($ResolvedPath)
    $Extension = [System.IO.Path]::GetExtension($ResolvedPath).ToLowerInvariant()
    $ContentType = $MimeTypes[$Extension]
    if (-not $ContentType) {
      $ContentType = "application/octet-stream"
    }

    Send-Response $Stream 200 "OK" $Bytes $ContentType
    $Client.Close()
  }
}
finally {
  $Server.Stop()
}
