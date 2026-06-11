$ftpUser = "if0_42129168"
$ftpPass = "2NEBtsBiGlAwB"
$ftpHost = "ftp://ftpupload.net/htdocs/english_bot"
$localDir = "c:\Users\User\Desktop\engilsh tili organ"

$files = @(
    "config.php",
    "bot.php",
    "cron.php",
    "database.sql",
    "functions.php",
    "setwebhook.php",
    "admin\index.php",
    "admin\dashboard.php",
    "admin\users.php",
    "admin\words.php",
    "admin\tests.php",
    "admin\broadcasts.php",
    "admin\settings.php",
    "admin\logout.php"
)

foreach ($file in $files) {
    $ftpUrl = "$ftpHost/$($file.Replace('\', '/'))"
    $localFile = "$localDir\$file"
    
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPass)
    
    Write-Host "Uploading $file..."
    try {
        $webclient.UploadFile($ftpUrl, $localFile)
        Write-Host "Successfully uploaded $file"
    } catch {
        Write-Host "Failed to upload $file : $_"
    }
}
