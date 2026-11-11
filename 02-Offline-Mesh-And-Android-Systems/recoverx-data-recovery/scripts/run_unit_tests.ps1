# RecoverX Unit Test Runner
# Solves Windows process-argument non-ASCII path encoding by using 8.3 short path

$junit = (Get-ChildItem -Path "$env:USERPROFILE\.gradle\caches\modules-2\files-2.1\junit\junit\4.13.2" -Filter "junit-4.13.2.jar" -Recurse | Select-Object -First 1).FullName
$hamcrest = (Get-ChildItem -Path "$env:USERPROFILE\.gradle\caches\modules-2\files-2.1\org.hamcrest\hamcrest-core\1.3" -Filter "hamcrest-core-1.3.jar" -Recurse | Select-Object -First 1).FullName
$kotlinStd = (Get-ChildItem -Path "$env:USERPROFILE\.gradle\caches\modules-2\files-2.1\org.jetbrains.kotlin\kotlin-stdlib" -Filter "kotlin-stdlib-2.*.jar" -Recurse | Select-Object -First 1).FullName

# Resolve short path for project root
$fso = New-Object -ComObject Scripting.FileSystemObject
$folder = $fso.GetFolder($PSScriptRoot + "\..")
$shortRoot = $folder.ShortPath

$testClasses = "$shortRoot\app\build\intermediates\built_in_kotlinc\debugUnitTest\compileDebugUnitTestKotlin\classes"
$appClasses = "$shortRoot\app\build\intermediates\built_in_kotlinc\debug\compileDebugKotlin\classes"

$cp = "$testClasses;$appClasses;$junit;$hamcrest;$kotlinStd"
$java = "C:\Program Files\Android\Android Studio\jbr\bin\java.exe"

Write-Host "Running RecoverX Unit Tests with Java 21..." -ForegroundColor Cyan
& $java -cp $cp org.junit.runner.JUnitCore com.recoverx.SignatureRegistryTest com.recoverx.FileCategorizerTest com.recoverx.CollisionResolverTest
