Import-Module AWSPowerShell.NetCore

$zdoomVersion = "2.8.1"
$zdoomUrl = "https://zdoom.org/files/zdoom/2.8/zdoom-$zdoomVersion.zip"
$zdoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/zdoom-Chris.ini"
$gzDoomVersion = "4.2.1"
$gzDoomVersionHyphenSeparator = $gzDoomVersion.replace(".", "-")
$gzDoomUrl = "https://github.com/coelckers/gzdoom/releases/download/g$gzDoomVersion/gzdoom-4-2-1-Windows-64bit.zip"
$gzDoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/gzdoom-Chris.ini"
$prBoomVersion = "2.5.1.4"
$prBoomUrl = "https://downloads.sourceforge.net/project/prboom-plus/prboom-plus/$prBoomVersion/prboom-plus-$prBoomVersion-win32.zip"
$prBoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/prboom-plus.cfg"
$glBoomVersion = "2.5.1.4"
$glBoomUrl = "https://downloads.sourceforge.net/project/prboom-plus/prboom-plus/$glBoomVersion/prboom-plus-$glBoomVersion-win32.zip"
$glBoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/glboom-plus.cfg"
$crispyDoomVersion = "5.6.3"
$crispyDoomUrl = "https://github.com/fabiangreffrath/crispy-doom/releases/download/crispy-doom-$crispyDoomVersion/crispy-doom-$crispyDoomVersion-win32.zip"
$crispyDoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/crispy-doom.cfg"
$doomRetroVersion = "3.0.5"
$doomRetroUrl = "https://github.com/bradharding/doomretro/releases/download/v$doomRetroVersion/doomretro-$doomRetroVersion-win64.zip"
$doomRetroConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/doomretro.cfg"
$marshmallowDoomVersion = "0.77"
$marshmallowDoomUrl = "http://www.marshmallowdoom.com/downloads/marshmallow-doom.zip"
$marshmallowDoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/doom/config/doomretro.cfg"
$doomRootPath = Join-Path -Path (Get-Item env:"USERPROFILE").Value -ChildPath "doom"
$sourcePortsPath = Join-Path -Path $doomRootPath -ChildPath "source-ports"
$configPath = Join-Path -Path $doomRootPath -ChildPath "config"
$iwadPath = Join-Path -Path $doomRootPath -ChildPath "iwads"
$wadPath = Join-Path -Path $doomRootPath -ChildPath "wads"
$modPath = Join-Path -Path $doomRootPath -ChildPath "mods"
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
    if (!(Test-Path $modPath)) {
        New-Item -ItemType Directory -Path $modPath
    }
    $local:launchersPath = Join-Path -Path $doomRootPath -ChildPath "launchers"
    if (!(Test-Path $launchersPath)) {
        New-Item -ItemType Directory -Path $launchersPath
    }
}

function InstallSourcePort {
    Param(
        [String]
        $DirectoryName,
        [String]
        $SourcePortUrl,
        [String]
        $ConfigUrl
    )

    $local:installPath = `
        Join-Path -Path $sourcePortsPath -ChildPath $DirectoryName
    $local:start = $SourcePortUrl.LastIndexOf('/') + 1
    $local:len = $SourcePortUrl.Length - $start
    $local:archiveName = $SourcePortUrl.Substring($start, $len)
    if (!(Test-Path $installPath)) {
        New-Item -ItemType Directory -Path $installPath
        cd $installPath
        curl.exe -L -O $SourcePortUrl
        7z e $archiveName
        rm $archiveName
        cd $configPath
        curl.exe -L -O $ConfigUrl
        cd $pwd
    }
}

function DownloadWad {
    Param(
        [String]
        $Name
    )

    $local:destination = Join-Path -Path $wadPath -ChildPath $Name
    if (!(Test-Path $destination)) {
        Copy-S3Object `
            -BucketName jacderida-games -Key wads/$Name -LocalFile $destination `
            -ProfileName s3
    }
}

function DownloadIwad {
    Param(
        [String]
        $Name
    )

    $local:destination = Join-Path -Path $iwadPath -ChildPath $Name
    if (!(Test-Path $destination)) {
        Copy-S3Object `
            -BucketName jacderida-games -Key iwads/$Name -LocalFile $destination `
            -ProfileName s3
    }
}

function DownloadMod {
    Param(
        [String]
        $Name
    )

    $local:destination = Join-Path -Path $modPath -ChildPath $Name
    if (!(Test-Path $destination)) {
        Copy-S3Object `
            -BucketName jacderida-games -Key mods/$Name -LocalFile $destination `
            -ProfileName s3
    }
}

CreateHomeDirectories
InstallSourcePort `
    -DirectoryName "crispy_doom-$crispyDoomVersion" `
    -SourcePortUrl $crispyDoomUrl `
    -ConfigUrl $crispyDoomConfigUrl
InstallSourcePort `
    -DirectoryName "doom_retro-$doomRetroVersion" `
    -SourcePortUrl $doomRetroUrl `
    -ConfigUrl $doomRetroConfigUrl
InstallSourcePort `
    -DirectoryName "gzdoom-$gzDoomVersion" `
    -SourcePortUrl $gzDoomUrl `
    -ConfigUrl $gzDoomConfigUrl
InstallSourcePort `
    -DirectoryName "zdoom-$zdoomVersion" `
    -SourcePortUrl $zdoomUrl `
    -ConfigUrl $zdoomConfigUrl
InstallSourcePort `
    -DirectoryName "prboom-$prBoomVersion" `
    -SourcePortUrl $prBoomUrl `
    -ConfigUrl $prBoomConfigUrl
InstallSourcePort `
    -DirectoryName "glboom-$glBoomVersion" `
    -SourcePortUrl $glBoomUrl `
    -ConfigUrl $glBoomConfigUrl
InstallSourcePort `
    -DirectoryName "marshmallow_doom-$marshmallowDoomVersion" `
    -SourcePortUrl $marshmallowDoomUrl `
    -ConfigUrl $marshmallowDoomConfigUrl
DownloadIwad -Name "DOOM.WAD"
DownloadIwad -Name "DOOM2.WAD"
DownloadWad -Name "SIGIL_v1_21.wad"
DownloadWad -Name "SIGIL_COMPAT_v1_21.wad"
DownloadWad -Name "PLUTONIA.WAD"
DownloadWad -Name "TNT.WAD"
DownloadWad -Name "HR.WAD"
DownloadWad -Name "hr2final.wad"
DownloadWad -Name "pk_doom_sfx.wad" # High resolution sound effects
DownloadWad -Name "D1SPFX19.WAD" # Minor sprite fixes for DOOM 1
DownloadWad -Name "D2SPFX19.WAD" # Minor sprite fixes for DOOM 2
DownloadMod -Name "SmoothDoom.pk3" # Smooth Doom for improved animations
DownloadMod -Name "BDoom632.pk3" # Beautiful Doom for improved animations and others
