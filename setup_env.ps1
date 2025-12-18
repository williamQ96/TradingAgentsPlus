param(
  [string]$VenvDir = 'tradingagents-venv',
  [string]$Req = 'requirements.txt',
  [string]$ReqDev = 'requirements-dev.txt',
  [switch]$Dev,
  [switch]$NoKernel,

  # Choose python version via Windows Python Launcher (py)
  # Examples: -Py 3.11  |  -Py 3.12
  [string]$Py = '',

  # Or specify a full path to python.exe
  # Example: -PyExe 'C:\Users\you\AppData\Local\Programs\Python\Python311\python.exe'
  [string]$PyExe = ''
)

$ErrorActionPreference = 'Stop'
function Say([string]$msg) { Write-Host $msg }

function Resolve-PythonCommand {
  param([string]$Py, [string]$PyExe)

  # 1) If user gave full python.exe path, use it
  if ($PyExe -ne '') {
    if (-not (Test-Path $PyExe)) { throw ('PyExe not found: ' + $PyExe) }
    return @{ Mode = 'exe'; Cmd = $PyExe; Args = @() }
  }

  # 2) If user gave a version like 3.11, prefer py launcher
  if ($Py -ne '') {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
      throw 'Python Launcher (py) not found, cannot use -Py. Install Python Launcher or pass -PyExe.'
    }
    # Validate version format a bit (allow 3, 3.11, 3.12 etc.)
    if ($Py -notmatch '^\d+(\.\d+)?$') { throw ('Invalid -Py value: ' + $Py + ' (use like 3.11)') }

    return @{ Mode = 'py'; Cmd = 'py'; Args = @('-' + $Py) }
  }

  # 3) Default behavior: prefer py -3 if available, else python
  if (Get-Command py -ErrorAction SilentlyContinue) {
    return @{ Mode = 'py'; Cmd = 'py'; Args = @('-3') }
  }
  if (Get-Command python -ErrorAction SilentlyContinue) {
    return @{ Mode = 'exe'; Cmd = 'python'; Args = @() }
  }

  throw 'Python not found. Install Python 3 first.'
}

# Decide python command for venv creation
$pyCmd = Resolve-PythonCommand -Py $Py -PyExe $PyExe

# 1) Create venv if missing
if (-not (Test-Path $VenvDir)) {
  Say ('Creating venv at: ' + $VenvDir)

  if ($pyCmd.Mode -eq 'py') {
    # Example: py -3.11 -m venv .venv
    & $pyCmd.Cmd @($pyCmd.Args) -m venv $VenvDir
  }
  else {
    # Example: C:\...\python.exe -m venv .venv  OR  python -m venv .venv
    & $pyCmd.Cmd -m venv $VenvDir
  }
}
else {
  Say ('venv exists: ' + $VenvDir)
}

# 2) Activate venv
$activate = Join-Path $VenvDir 'Scripts\Activate.ps1'
if (-not (Test-Path $activate)) { throw ('Activation script not found: ' + $activate) }
. $activate

# 3) Show python path + version
$pyExePath = python -c 'import sys; print(sys.executable)'
$pyVer = python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'
Say ('Using python: ' + $pyExePath)
Say ('Python version: ' + $pyVer)

# 4) Upgrade pip tooling
Say 'Upgrading pip / wheel / setuptools ...'
python -m pip install --upgrade pip wheel setuptools

# 5) Install requirements
if (Test-Path $Req) {
  Say ('Installing: ' + $Req)
  pip install -r $Req
}
else {
  Say ('WARNING: not found, skipping: ' + $Req)
}

# 6) Install dev requirements (optional)
if ($Dev -or (Test-Path $ReqDev)) {
  if (Test-Path $ReqDev) {
    Say ('Installing dev: ' + $ReqDev)
    pip install -r $ReqDev
  }
  else {
    Say ('WARNING: not found, skipping: ' + $ReqDev)
  }
}

# 7) Register Jupyter kernel (optional)
if (-not $NoKernel) {
  $proj = Split-Path -Leaf (Get-Location)
  $kernelName = ($proj -replace '[^a-zA-Z0-9_-]', '-') + '-venv'
  Say ('Registering Jupyter kernel: ' + $kernelName)

  pip install -q ipykernel
  python -m ipykernel install --user --name $kernelName --display-name ('Python (' + $proj + ')')
}

# 8) Done message
$activatePath = Join-Path $VenvDir 'Scripts\Activate.ps1'
Say ''
Say 'Done. Next:'
Say ('  Activate: ' + $activatePath)
Say '  Run:      python <your_script>.py'
Say '  Jupyter:  jupyter lab'
