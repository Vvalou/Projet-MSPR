while ($true) {
    Clear-Host
    Write-Host "=== TEST MODULE SAUVEGARDE WMS ===`n"
    Write-Host "1) Afficher le contenu de la table inventory"
    Write-Host "2) Tester la sauvegarde SQL complete"
    Write-Host "3) Tester l'export CSV de la table inventory"
    Write-Host "0) Quitter`n"

    $choice = Read-Host "Votre choix"

    switch ($choice) {
        "1" {
            docker exec -it wms-db mysql -uwms_backup -pBackupWMS2025 wms -e "SELECT * FROM inventory;"
            Pause
        }
        "2" {
            powershell -File .\src\Backup-Wms.ps1 -Mode Full
            Pause
        }
        "3" {
            powershell -File .\src\Backup-Wms.ps1 -Mode Table -TableName inventory
            Pause
        }
        "0" { break }
        default {
            Write-Host "Choix invalide."
            Pause
        }
    }
}

