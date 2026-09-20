$ErrorActionPreference='Stop'
& "$PSScriptRoot\..\.venv\Scripts\python.exe" -m pytest -q -p no:cacheprovider
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
$hostTestBinary=Join-Path $PSScriptRoot "..\firmware\esp32\tests\tark_host_protocol_tests_$PID.exe"
& 'C:\msys64\ucrt64\bin\gcc.exe' -std=c11 -Wall -Wextra -Werror -I "$PSScriptRoot\..\firmware\esp32\main\protocol" -I "$PSScriptRoot\..\firmware\esp32\main\command" -I "$PSScriptRoot\..\firmware\esp32\main\hardware" -I "$PSScriptRoot\..\firmware\esp32\main\safety" "$PSScriptRoot\..\firmware\esp32\tests\host_test.c" "$PSScriptRoot\..\firmware\esp32\main\protocol\tark_protocol.c" "$PSScriptRoot\..\firmware\esp32\main\protocol\command_payload.c" "$PSScriptRoot\..\firmware\esp32\main\command\command_supervisor.c" "$PSScriptRoot\..\firmware\esp32\main\hardware\motor_driver.c" "$PSScriptRoot\..\firmware\esp32\main\hardware\encoder.c" "$PSScriptRoot\..\firmware\esp32\main\safety\watchdog.c" -lm -o $hostTestBinary
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $hostTestBinary
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
$serviceTestBinary=Join-Path $PSScriptRoot "..\firmware\esp32\tests\tark_host_service_tests_$PID.exe"
& 'C:\msys64\ucrt64\bin\gcc.exe' -std=c11 -Wall -Wextra -Werror -I "$PSScriptRoot\..\firmware\esp32\main\protocol" -I "$PSScriptRoot\..\firmware\esp32\main\command" "$PSScriptRoot\..\firmware\esp32\tests\task7b_host_test.c" "$PSScriptRoot\..\firmware\esp32\main\protocol\tark_protocol.c" "$PSScriptRoot\..\firmware\esp32\main\protocol\command_payload.c" "$PSScriptRoot\..\firmware\esp32\main\protocol\response.c" "$PSScriptRoot\..\firmware\esp32\main\protocol\service.c" "$PSScriptRoot\..\firmware\esp32\main\command\command_supervisor.c" -lm -o $serviceTestBinary
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $serviceTestBinary
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& "$PSScriptRoot\test_frontend.ps1"
Remove-Item -LiteralPath $hostTestBinary,$serviceTestBinary -Force -ErrorAction SilentlyContinue
