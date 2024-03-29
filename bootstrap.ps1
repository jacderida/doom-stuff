Import-Module AWSPowerShell.NetCore

$zdoomVersion = "2.8.1"
$zdoomUrl = "https://zdoom.org/files/zdoom/2.8/zdoom-$zdoomVersion.zip"
$zdoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/config/zdoom-Chris.ini"
$gzDoomVersion = "4.4.2"
$gzDoomVersionHyphenSeparator = $gzDoomVersion.replace(".", "-")
$gzDoomUrl = "https://github.com/coelckers/gzdoom/releases/download/g$gzDoomVersion/gzdoom-$gzDoomVersionHyphenSeparator-Windows-64bit.zip"
$gzDoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/config/gzdoom-Chris.ini"
$prBoomVersion = "2.5.1.5"
$prBoomUrl = "http://prboom-plus.sourceforge.net/prboom-plus-$prBoomVersion.r4526-win32.zip"
$prBoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/config/prboom-plus.cfg"
$glBoomVersion = "2.5.1.5"
$glBoomUrl = "http://prboom-plus.sourceforge.net/prboom-plus-$glBoomVersion.r4526-win32.zip"
$glBoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/config/glboom-plus.cfg"
$crispyDoomVersion = "5.10.0"
$crispyDoomUrl = "https://github.com/fabiangreffrath/crispy-doom/releases/download/crispy-doom-$crispyDoomVersion/crispy-doom-$crispyDoomVersion-win32.zip"
$crispyDoomConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/config/crispy-doom.cfg"
$dsdaDoomVersion = "0.13.0"
$dsdaDoomUrl = "https://jacderida-software.s3-eu-west-1.amazonaws.com/dsda-doom-$dsdaDoomVersion.zip"
$dsdaConfigUrl = ""
$doomRetroVersion = "3.0.5"
$doomRetroUrl = "https://github.com/bradharding/doomretro/releases/download/v$doomRetroVersion/doomretro-$doomRetroVersion-win64.zip"
$doomRetroConfigUrl = "https://raw.githubusercontent.com/jacderida/game-stuff/master/config/doomretro.cfg"
$doomRootPath = Join-Path -Path (Get-Item env:"USERPROFILE").Value -ChildPath "doom"
$sourcePortsPath = Join-Path -Path $doomRootPath -ChildPath "source-ports"
$configPath = Join-Path -Path $doomRootPath -ChildPath "config"
$iwadPath = Join-Path -Path $doomRootPath -ChildPath "iwads"
$wadPath = Join-Path -Path $doomRootPath -ChildPath "wads"
$demoPath = Join-Path -Path $doomRootPath -ChildPath "demos"
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
    if (!(Test-Path $demoPath)) {
        New-Item -ItemType Directory -Path $demoPath
    }
    $local:launchersPath = Join-Path -Path $doomRootPath -ChildPath "launchers"
    if (!(Test-Path $launchersPath)) {
        New-Item -ItemType Directory -Path $launchersPath
    }
    $local:demoLaunchersPath = Join-Path -Path $doomRootPath -ChildPath "demo-launchers"
    if (!(Test-Path $demoLaunchersPath)) {
        New-Item -ItemType Directory -Path $demoLaunchersPath
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

function InstallUtils {
    $local:utilsPath = Join-Path -Path $doomRootPath -ChildPath "utils"
    if (!(Test-Path $utilsPath)) {
        New-Item -ItemType Directory -Path $utilsPath
    }

    $local:currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if (!($currentPath -like "*$utilsPath*")) {
        echo "Adding $utilsPath to PATH"
        $currentPath += ";$utilsPath"
        [Environment]::SetEnvironmentVariable("PATH", $currentPath, "User")
    }

    $local:oggEncArchiveName = "oggenc2.88-1.3.7-x64.zip"
    $local:oggEncUrl = "http://www.rarewares.org/files/ogg/$oggEncArchiveName"
    $local:oggEncPath = Join-Path -Path $utilsPath -ChildPath "oggenc2.exe"
    if (!(Test-Path $oggEncPath)) {
        echo "Downloading oggenc2"
        cd $utilsPath
        curl.exe -L -O $oggEncUrl
        7z e $oggEncArchiveName
        rm $oggEncArchiveName
        cd $pwd
    }

    $local:x264FileName = "x264-r3018-db0d417.exe"
    $local:x264Url = "https://artifacts.videolan.org/x264/release-win64/x264-r3018-db0d417.exe"
    $local:x264TempPath = Join-Path -Path $utilsPath -ChildPath $x264FileName
    $local:x264Path = Join-Path -Path $utilsPath -ChildPath "x264.exe"
    if (!(Test-Path $x264Path)) {
        echo "Downloading x264"
        cd $utilsPath
        curl.exe -L -O $x264Url
        Rename-Item -Path $x264TempPath -NewName "x264.exe"
        cd $pwd
    }

    $local:mkvMergeVersion = "49.0.0"
    $local:mkvMergeArchiveName = "mkvtoolnix-64-bit-$mkvMergeVersion.7z"
    $local:mkvMergeUrl = "https://jacderida-software.s3-eu-west-1.amazonaws.com/$mkvMergeArchiveName"
    $local:mkvMergePath = Join-Path -Path $utilsPath -ChildPath "mkvmerge.exe"
    if (!(Test-Path $mkvMergePath)) {
        echo "Downloading mkvmerge"
        cd $utilsPath
        curl.exe -L -O $mkvMergeUrl
        7z x $mkvMergeArchiveName
        $local:mkvMergeTempPath = Join-Path `
            -Path $utilsPath `
            -ChildPath "\mkvtoolnix\mkvmerge.exe"
        echo "$mkvMergeTempPath"
        Move-Item -Path $mkvMergeTempPath -Destination $mkvMergePath
        rm $mkvMergeArchiveName
        Remove-Item -Recurse -Force "mkvtoolnix"
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

function DownloadMasterLevels {
    DownloadWad -Name "ATTACK.WAD"
    DownloadWad -Name "CANYON.WAD"
    DownloadWad -Name "CATWALK.WAD"
    DownloadWad -Name "COMBINE.WAD"
    DownloadWad -Name "FISTULA.WAD"
    DownloadWad -Name "GARRISON.WAD"
    DownloadWad -Name "MANOR.WAD"
    DownloadWad -Name "PARADOX.WAD"
    DownloadWad -Name "SUBSPACE.WAD"
    DownloadWad -Name "SUBTERRA.WAD"
    DownloadWad -Name "TTRAP.WAD"
    DownloadWad -Name "VIRGIL.WAD"
    DownloadWad -Name "MINOS.WAD"
    DownloadWad -Name "BLOODSEA.WAD"
    DownloadWad -Name "MEPHISTO.WAD"
    DownloadWad -Name "NESSUS.WAD"
    DownloadWad -Name "GERYON.WAD"
    DownloadWad -Name "VESPERAS.WAD"
    DownloadWad -Name "BLACKTWR.WAD"
    DownloadWad -Name "TEETH.WAD"
    DownloadWad -Name "TEETH.WAD"
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
    -DirectoryName "dsda-$dsdaDoomVersion" `
    -SourcePortUrl $dsdaDoomUrl `
    -ConfigUrl $glBoomConfigUrl
InstallUtils
DownloadIwad -Name "DOOM.WAD"
DownloadIwad -Name "DOOM2.WAD"
DownloadIWad -Name "PLUTONIA.WAD"
DownloadIWad -Name "TNT.WAD"
DownloadMasterLevels
DownloadWad -Name "SIGIL_v1_21.wad"
DownloadWad -Name "SIGIL_COMPAT_v1_21.wad"
DownloadWad -Name "HR.WAD"
DownloadWad -Name "hr2final.wad"
DownloadWad -Name "oku2v31.wad"
DownloadWad -Name "Eviternity.wad"
DownloadWad -Name "AV.WAD"
DownloadWad -Name "btsx_e1a.wad"
DownloadWad -Name "btsx_e1b.wad"
DownloadWad -Name "sunlust.wad"
DownloadWad -Name "D2SPFX19-sunlust.WAD"
DownloadWad -Name "bastionv0.9.pk3"
DownloadWad -Name "ANTA_REQ.wad"
DownloadWad -Name "JPCP.wad"
DownloadWad -Name "JPCP_HUD.wad"
DownloadWad -Name "pk_doom_sfx.wad" # Subtle high resolution sound effect improvements
DownloadWad -Name "D1SPFX19.WAD" # Minor sprite fixes for DOOM 1
DownloadWad -Name "D2SPFX19.WAD" # Minor sprite fixes for DOOM 2
DownloadWad -Name "DSPLASMA.WAD" # Plasma Rifle sound extracted from Sunlust
DownloadMod -Name "SmoothDoom.pk3" # Smooth Doom for improved animations
DownloadMod -Name "BDoom632.pk3" # Beautiful Doom for improved animations and others
DownloadMod -Name "idclever-starter.pk3" # Pistol starts for GZDoom
DownloadMod -Name "fullscrn_huds.pk3" # Better alternate HUD for GZDoom
DownloadMod -Name "perk_enhanced.pk3" # Slightly enhanced weapon animations
DownloadMod -Name "decorate.txt" # Disables Lost Souls in enemy count in GZDoom
