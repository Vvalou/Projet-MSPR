param(
    [ValidateSet("Full","Table")]
    [string]$Mode,
    [string]$TableName = "inventory"
)

#config 
$timestamp    = Get-Date -Format "yyyyMMdd_HHmmss"
$backupSqlDir = ".\backups\sql"
$backupCsvDir = ".\backups\csv"
$logDir       = ".\logs"

New-Item -ItemType Directory -Force -Path $backupSqlDir,$backupCsvDir,$logDir | Out-Null

$logFile = Join-Path $logDir "wms_backup_$timestamp.log"

function Write-LogJson {
    param($status,$action,$details)
    $entry = [pscustomobject]@{
        timestamp = (Get-Date).ToString("s")
        module    = "WMSBackup"
        action    = $action
        status    = $status
        details   = $details
    }
    $entry | ConvertTo-Json -Compress | Add-Content -Path $logFile
}

# SAUVEGARDE SQL COMPLÈTE
if ($Mode -eq "Full") {
    $sqlFile = Join-Path $backupSqlDir "wms_full_backup_$timestamp.sql"

    docker exec wms-db mysqldump -uwms_backup -pBackupWMS2025 wms > $sqlFile

    if ($LASTEXITCODE -eq 0) {
        Write-LogJson "success" "full_sql" @{ file = $sqlFile }
        Write-Host "Sauvegarde SQL OK -> $sqlFile"
        exit 0
    }
    else {
        Write-LogJson "error" "full_sql" @{ file = $sqlFile }
        Write-Host "Échec sauvegarde SQL"
        exit 1
    }
}

# EXPORT CSV
if ($Mode -eq "Table") {
    $rawFile = Join-Path $backupCsvDir "${TableName}_raw_$timestamp.tsv"
    $csvFile = Join-Path $backupCsvDir "${TableName}_export_$timestamp.csv"

    $sql = @"
SELECT i.id,
       w.name       AS warehouse_code,
       w.location   AS ville_entrepot,
       e.libelle    AS nom_equipement,
       e.type       AS type_equipement,
       i.product_code,
       i.quantity,
       i.created_at
FROM inventory i
JOIN warehouses w  ON i.warehouse_id = w.id
JOIN equipements e ON i.product_code = e.code;
"@

    docker exec wms-db mysql -uwms_backup -pBackupWMS2025 wms -e "$sql" > $rawFile

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur lors de l'exécution de la requête SQL pour l'export CSV."
        Write-LogJson "error" "table_csv" @{ table = $TableName; file = $csvFile }
        exit 1
    }

    $data = Get-Content $rawFile | ConvertFrom-Csv -Delimiter "`t"

    $dataRenamed = $data | Select-Object @{
            Name="id_ligne";        Expression={$_.id}
        }, @{
            Name="code_entrepot";   Expression={$_.warehouse_code}
        }, @{
            Name="ville";           Expression={$_.ville_entrepot}
        }, @{
            Name="nom_equipement";  Expression={$_.nom_equipement}
        }, @{
            Name="type_equipement"; Expression={$_.type_equipement}
        }, @{
            Name="reference";       Expression={$_.product_code}
        }, @{
            Name="quantite";        Expression={$_.quantity}
        }, @{
            Name="date_creation";   Expression={$_.created_at}
        }

    $dataRenamed | Export-Csv -Path $csvFile -Delimiter ';' -Encoding UTF8 -NoTypeInformation
    Remove-Item $rawFile

    Write-LogJson "success" "table_csv" @{ table = $TableName; file = $csvFile }
    Write-Host "Export CSV OK (inventory avec villes + équipements) -> $csvFile"
    exit 0
}
