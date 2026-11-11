$fso = New-Object -ComObject Scripting.FileSystemObject
$folder = $fso.GetFolder($PSScriptRoot)
$shortPath = $folder.ShortPath

$java = "C:\Program Files\Android\Android Studio\jbr\bin\java.exe"
if (-not (Test-Path $java)) {
    if ($env:JAVA_HOME -and (Test-Path "$env:JAVA_HOME\bin\java.exe")) {
        $java = "$env:JAVA_HOME\bin\java.exe"
    } else {
        $java = "java"
    }
}

Push-Location $shortPath
try {
    & $java -jar "$shortPath\gradle\wrapper\gradle-wrapper.jar" -p "$shortPath" @args
} finally {
    Pop-Location
}
