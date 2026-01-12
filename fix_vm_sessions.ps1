# Script de correction des problèmes de sessions VM
# À exécuter en tant qu'administrateur sur la VM

Write-Host "=== CORRECTION DES PROBLÈMES DE SESSIONS VM ===" -ForegroundColor Green

# 1. Augmenter la mémoire virtuelle
Write-Host "1. Configuration de la mémoire virtuelle..." -ForegroundColor Yellow
$pageFile = Get-WmiObject -Class Win32_PageFileSetting
if ($pageFile) {
    $pageFile.InitialSize = 8192  # 8 GB
    $pageFile.MaximumSize = 16384 # 16 GB
    $pageFile.Put()
    Write-Host "   Mémoire virtuelle configurée: 8-16 GB" -ForegroundColor Green
}

# 2. Redémarrer le service DWM
Write-Host "2. Redémarrage du Desktop Window Manager..." -ForegroundColor Yellow
Stop-Service -Name "UxSms" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Start-Service -Name "UxSms" -ErrorAction SilentlyContinue
Write-Host "   Service DWM redémarré" -ForegroundColor Green

# 3. Nettoyer les fichiers temporaires
Write-Host "3. Nettoyage des fichiers temporaires..." -ForegroundColor Yellow
Get-ChildItem -Path "C:\Windows\Temp" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Path "$env:TEMP" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "   Fichiers temporaires nettoyés" -ForegroundColor Green

# 4. Réparer les composants système
Write-Host "4. Réparation des composants système..." -ForegroundColor Yellow
sfc /scannow
Write-Host "   Vérification système terminée" -ForegroundColor Green

# 5. Redémarrer les services critiques
Write-Host "5. Redémarrage des services critiques..." -ForegroundColor Yellow
$services = @("Themes", "AudioSrv", "AudioEndpointBuilder", "Spooler")
foreach ($service in $services) {
    Restart-Service -Name $service -ErrorAction SilentlyContinue
    Write-Host "   Service $service redémarré" -ForegroundColor Green
}

# 6. Optimiser les performances
Write-Host "6. Optimisation des performances..." -ForegroundColor Yellow
# Désactiver les effets visuels pour réduire la charge
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2
Write-Host "   Effets visuels optimisés" -ForegroundColor Green

Write-Host "=== CORRECTION TERMINÉE ===" -ForegroundColor Green
Write-Host "Redémarrez la VM pour appliquer tous les changements." -ForegroundColor Cyan
