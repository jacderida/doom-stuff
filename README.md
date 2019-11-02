# Game Stuff

Little repo for game scripts and configurations.

## Doom

There are scripts here that will setup a Windows machine for playing Doom and will generate 'launchers' for starting each level in a game with a pistol.

### Prerequisites

For running these scripts:

* Install the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
* Install [Powershell Core](https://github.com/PowerShell/PowerShell/releases)
* Install the AWS tools for Powershell: `Install-Module -Name AWSPowerShell.NetCore`
* Use the module: `Import-Module -Name AWSPowerShell.NetCore`
* Setup AWS credentials for S3: `Set-AWSCredential -AccessKey <key> -SecretKey <key> -StoreAs s3`

### Run Scripts

After this is done, you can run `doom\bootstrap.ps1`. This script will:

* Create a `doom` directory in `%USERPROFILE%` with self explanatory sub-directories
* Install various source ports
* Download source port configuration files from this repo
* Download `DOOM.WAD` and `DOOM2.WAD` iwad files
* Download various pwad files
* Download various modifications

Once that's been done, there's a little Python script that can generate the launchers. Launchers are just a set of batch files for each game, one for each mission (note: a 'game' here really refers to a WAD, e.g. SIGIL.WAD, not Doom or Doom 2 (though both of those happen to be a game too)). These batch files allow you to quickly start any level in the game with a pistol.

To run the script you need to use WSL, which should have an Ubuntu environment that comes with a Python installation. Run the `generate-game-batch.py` script and follow the prompts.
