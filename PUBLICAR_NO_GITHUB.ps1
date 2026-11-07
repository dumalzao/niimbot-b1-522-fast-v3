# Publica ESTE pacote como um NOVO repositorio publico no GitHub.
# Requisitos: Git e GitHub CLI (gh) instalados; gh auth login efetuado.
# Execute conscientemente: esta acao publica codigo, documentos e imagem de teste.
param(
    [string]$Owner = "dumalzao",
    [string]$RepoName = "niimbot-b1-522-fast-v3"
)
$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git nao localizado. Instale Git for Windows: https://git-scm.com/download/win"
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI nao localizado. Instale 'GitHub CLI' e execute 'gh auth login'."
}
& gh auth status
if ($LASTEXITCODE -ne 0) {
    throw "Autenticacao GitHub ausente. Execute: gh auth login"
}

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoDir

if (Test-Path '.git') {
    throw 'Esta pasta ja tem um repositorio Git; para evitar publicacao acidental, interrompido.'
}

$Forbidden = @(Get-ChildItem -File -Recurse | Where-Object {
    $_.Extension -in @('.bin','.hex','.uf2','.dfu','.fw','.elf','.img','.dump','.dmp')
})
if ($Forbidden.Count -gt 0) {
    throw 'Arquivos de firmware encontrados nesta pasta. Remova-os antes de publicar.'
}

$Allowed = @(
    '.gitignore', 'LICENSE', 'README.md', 'README.en.md', 'CONTRIBUTING.md',
    'patch_b1_522_v3_corrige_escala.py', 'PUBLICAR_NO_GITHUB.ps1',
    'tests/teste_b1_522_v3_script.py',
    'docs/ANALISE_TECNICA.md', 'docs/TESTES_E_LIMITACOES.md',
    'examples/label-40x30-code128.png', '.github/ISSUE_TEMPLATE/relato-de-teste.md'
)
foreach ($File in $Allowed) {
    if (-not (Test-Path $File)) { throw "Arquivo obrigatorio ausente: $File" }
}

$Check = Read-Host "Vai criar PUBLICAMENTE $Owner/$RepoName. Digite PUBLICAR para confirmar"
if ($Check -cne 'PUBLICAR') {
    Write-Host 'Operacao cancelada, nenhuma publicacao realizada.'
    exit 1
}

& git init -b main
if ($LASTEXITCODE -ne 0) { throw 'git init falhou' }
foreach ($File in $Allowed) {
    & git add -- $File
    if ($LASTEXITCODE -ne 0) { throw "git add falhou para $File" }
}
& git commit -m 'Publica patch reprodutivel B1 5.22 FAST V3 e documentacao'
if ($LASTEXITCODE -ne 0) { throw 'git commit falhou. Configure user.name e user.email no Git se necessario.' }

& gh repo create "$Owner/$RepoName" --public --source . --remote origin --push --description 'NIIMBOT B1 5.22 FAST V3: patch de impressao rapida sem RFID, com escala corrigida (codigo e documentacao; sem firmware proprietario)'
if ($LASTEXITCODE -ne 0) { throw 'Criacao/publicacao falhou. Nao execute novamente sem verificar o repositorio no GitHub.' }

Write-Host "Publicado: https://github.com/$Owner/$RepoName"
