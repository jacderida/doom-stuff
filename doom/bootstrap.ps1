$zdoomVersion = "2.8.1"
$zdoomUrl = "https://zdoom.org/files/zdoom/2.8/zdoom-$zdoomVersion.zip"
$gzDoomVersion = "4.2.1"
$gzDoomVersionHyphenSeparator = $gzDoomVersion.replace(".", "-")
$gzDoomUrl = "https://github.com/coelckers/gzdoom/releases/download/g$gzDoomVersion/gzdoom-4-2-1-Windows-64bit.zip"
$prBoomVersion = "2.5.1.4"
$prBoomUrl = "https://downloads.sourceforge.net/project/prboom-plus/prboom-plus/$prBoomVersion/prboom-plus-$prBoomVersion-win32.zip"
$crispyDoomVersion = "5.6.3"
$crispyDoomUrl = "https://github.com/fabiangreffrath/crispy-doom/releases/download/crispy-doom-$crispyDoomVersion/crispy-doom-$crispyDoomVersion-win32.zip"
$crispyDoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/crispy-doom-custom.cfg"
$doomRetroVersion = "3.0.5"
$doomRetroUrl = "https://github.com/bradharding/doomretro/releases/download/v$doomRetroVersion/doomretro-$doomRetroVersion-win64.zip"

$doomRootPath = Join-Path -Path (Get-Item env:"USERPROFILE").Value -ChildPath "doom"
$sourcePortsPath = Join-Path -Path $doomRootPath -ChildPath "source-ports"
$configPath = Join-Path -Path $doomRootPath -ChildPath "config"
$iwadPath = Join-Path -Path $doomRootPath -ChildPath "iwad"
$wadPath = Join-Path -Path $doomRootPath -ChildPath "wad"
$pwd = Get-Location

function CreateHomeDirectories {
    if (!(Test-Path $doomRootPath)) {
        New-Item -ItemType Directory -Path $doomRootPath
    }
    if (!(Test-Path $sourcePortsPath)) {
        New-Item -ItemType Directory -Path $sourcePortsPath
    }
    if (!(Test-Path $configPath)) {
        New-Item -ItemType Directory -Path $configPath
    }
    if (!(Test-Path $iwadPath)) {
        New-Item -ItemType Directory -Path $iwadPath
    }
    if (!(Test-Path $wadPath)) {
        New-Item -ItemType Directory -Path $wadPath
    }
    $local:launchersPath = Join-Path -Path $doomRootPath -ChildPath "launchers"
    if (!(Test-Path $launchersPath)) {
        New-Item -ItemType Directory -Path $launchersPath
    }
}

function InstallCrispyDoom {
    $local:installPath = `
        Join-Path -Path $sourcePortsPath -ChildPath "crispy_doom-$crispyDoomVersion"
    if (!(Test-Path $installPath)) {
        New-Item -ItemType Directory -Path $installPath
        cd $installPath
        curl.exe -L -O $crispyDoomUrl
        7z e crispy-doom-$crispyDoomVersion-win32.zip
        rm crispy-doom-$crispyDoomVersion-win32.zip
        cd $configPath
        curl.exe -L -O $crispyDoomConfigUrl
        cd $pwd
    }
}

function InstallDoomRetro {
    $local:installPath = `
        Join-Path -Path $sourcePortsPath -ChildPath "doom_retro-$doomRetroVersion"
    if (!(Test-Path $installPath)) {
        New-Item -ItemType Directory -Path $installPath
        cd $installPath
        curl.exe -L -O $doomRetroUrl
        7z e doomretro-$doomRetroVersion-win64.zip
        rm doomretro-$doomRetroVersion-win64.zip
        cd $pwd
    }
}

CreateHomeDirectories
InstallCrispyDoom
InstallDoomRetro
