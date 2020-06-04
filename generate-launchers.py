#!/usr/bin/env python3

import csv
import glob
import operator
import os
import shutil
import sys
from abc import ABC
from collections import namedtuple


class SourcePort(ABC):
    def __init__(self, name, friendly_name, config_name, exe_name, install_path, version, doom_config):
        self.friendly_name = friendly_name
        self.name = name
        self.config_name = config_name
        self.install_path = install_path
        self.exe_name = exe_name
        self.exe_path = '{0}\\{1}'.format(install_path, self.exe_name)
        self.version = version
        self.doom_config = doom_config
        self.configurations = ['music', 'nomusic', 'nomonsters']

    def get_configurations(self):
        return self.configurations

    def get_launch_batch_commands(self, game, configuration):
        commands = []
        [commands.append(x) for x in self._get_pre_launch_config_commands()]
        commands.append(self._get_game_launch_command(game, None, None, configuration))
        [commands.append(x) for x in self.get_post_game_config_commands(game, configuration)]
        return commands

    def get_map_launch_batch_commands(self, game, episode, mission, configuration):
        commands = []
        if configuration == 'record':
            [commands.append(x) for x in self._get_pre_launch_record_commands()]
        [commands.append(x) for x in self._get_pre_launch_config_commands()]
        commands.append(self._get_game_launch_command(game, episode, mission, configuration))
        [commands.append(x) for x in self.get_post_game_config_commands(game, configuration)]
        return commands

    def get_mod_options(self, configuration):
        return ''

    def get_post_game_config_commands(self, game, configuration):
        return [
            'del {0}'.format(self.config_name),
            'cd %start%'
        ]

    def get_game_options(self, game, mission):
        """
        There are a couple of hard coded cases here for rare exceptions. The first is for
        Back to Saturn X, which for some reason has an additional WAD file. The second is
        for the 'Master Levels' compilation, which distributes each map as a separate WAD file.
        """
        options = '-config {0} '.format(self.config_name)
        options += '-iwad {0}\\{1} '.format(self.doom_config.iwad_path, game.iwad)
        options += '-file {0}\\{1} '.format(self.doom_config.wad_path, game.pwad)
        if game.pwad == 'btsx_e1a.wad':
            options += '-file {0}\\{1} '.format(self.doom_config.wad_path, 'btsx_e1b.wad')
        if game.name == 'Master Levels for Doom II':
            options += '-file {0}\\{1} '.format(self.doom_config.wad_path, mission.wad)
        return options

    def get_misc_options(self, configuration):
        options = '-fullscreen '
        if configuration == 'nomusic':
            options += '-nomusic '
        elif configuration == 'nomonsters':
            options += '-nomonsters '
        return options

    def get_skill_option(self):
        return '-skill 4 '

    def get_warp_option(self, game, episode, mission):
        if game.name == 'Master Levels for Doom II':
            return '-warp 01 '
        elif game.iwad == 'DOOM2.WAD' or game.iwad == 'TNT.WAD' or game.iwad == 'PLUTONIA.WAD':
            return '-warp {0} '.format(str(mission.level).zfill(2))
        elif game.iwad == 'DOOM.WAD':
            return '-warp {0} {1} '.format(episode.number, mission.number)
        raise ValueError('iwad {0} not supported yet'.format(game.iwad))

    def get_low_priority_wads(self, game):
        options = ''
        if game.iwad == 'DOOM.WAD':
            options += '-file {0}\\D1SPFX19.WAD '.format(self.doom_config.wad_path)
        else:
            options += '-file {0}\\D2SPFX19.WAD '.format(self.doom_config.wad_path)
        options += '-file {0}\\pk_doom_sfx.wad '.format(self.doom_config.wad_path)
        options += '-file {0}\\DSPLASMA.wad '.format(self.doom_config.wad_path)
        return options

    def _get_game_launch_command(self, game, episode, mission, configuration):
        launch_command = '{0} '.format(self.exe_name)
        launch_command += self.get_game_options(game, mission)
        mod_options = self.get_mod_options(configuration)
        if mod_options:
            launch_command += mod_options
        launch_command += self.get_misc_options(configuration)
        if episode and mission:
            launch_command += self._get_map_specific_options(game, episode, mission)
        if configuration == 'record':
            launch_command += self.get_recording_options(game, episode, mission)
        launch_command += self.get_low_priority_wads(game)
        return launch_command.strip()

    def _get_pre_launch_record_commands(self):
        commands = []
        commands.append(
            'For /f "tokens=1-4 delims=/ " %%a in (\'date /t\') do (set mydate=%%c-%%b-%%a)')
        commands.append(
            'For /f "tokens=1-2 delims=/:" %%a in (\'time /t\') do (set mytime=%%a%%b)')
        commands.append(
            'set datetime=%mydate%-%mytime%')
        return commands

    def _get_pre_launch_config_commands(self):
        commands = []
        commands.append('set start=%cd%')
        commands.append('copy {0}\\{1} {2}\\{3} /Y'.format(
            self.doom_config.config_path,
            self.config_name,
            self.install_path,
            self.config_name))
        commands.append('cd {0}'.format(self.install_path))
        return commands

    def _get_map_specific_options(self, game, episode, mission):
        map_options = self.get_skill_option()
        map_options += self.get_warp_option(game, episode, mission)
        return map_options


class CrispyDoomSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'crispy', 'Crispy Doom', 'crispy-doom.cfg',
            'crispy-doom.exe', install_path, version, doom_config)


class MarshmallowDoomSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'marshmallow', 'Marshmallow Doom', 'marshmallow-doom.cfg',
            'marshmallow-doom.exe', install_path, version, doom_config)


class DoomRetroSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'retro', 'Doom Retro', 'doomretro.cfg',
            'doomretro.exe', install_path, version, doom_config)

    def get_misc_options(self, configuration):
        options = '-fullscreen '
        options += '-pistolstart '
        if configuration == 'nomusic':
            options += '-nomusic '
        return options

    def get_warp_option(self, game, episode, mission):
        return '-warp E{0}M{1} '.format(episode.number, mission.number)


class BoomSourcePort(SourcePort):
    def get_game_options(self, game, mission):
        options = '-iwad {0}\\{1} '.format(self.doom_config.iwad_path, game.iwad)
        options += '-file {0}\\{1} '.format(self.doom_config.iwad_path, game.pwad)
        if game.pwad == 'btsx_e1a.wad':
            options += '-file {0}\\{1} '.format(self.doom_config.wad_path, 'btsx_e1b.wad')
        if game.name == 'Master Levels for Doom II':
            options += '-file {0}\\{1} '.format(self.doom_config.wad_path, mission.wad)
        options += '-complevel {0} '.format(game.complevel)
        return options

    def get_misc_options(self, configuration):
        options = '-nowindow -noaccel '
        if configuration == 'nomusic':
            options += '-nomusic '
        return options


class PrBoomSourcePort(BoomSourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'prboom', 'PRBoom-plus', 'prboom-plus.cfg',
            'prboom-plus.exe', install_path, version, doom_config)


class GlBoomSourcePort(BoomSourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'glboom', 'GLBoom-plus', 'glboom-plus.cfg',
            'glboom-plus.exe', install_path, version, doom_config)


class GzDoomSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'gzdoom', 'GZDoom', 'gzdoom-Chris.ini',
            'gzdoom.exe', install_path, version, doom_config)
        self.configurations = [
            'music', 'nomusic', 'smooth', 'beautiful', 'nomonsters', 'record']

    def get_mod_options(self, configuration):
        options = ''
        if configuration == 'smooth':
            options += '-file {0}\\{1} '.format(self.doom_config.mod_path, 'SmoothDoom.pk3')
        elif configuration == 'beautiful':
            options += '-file {0}\\{1} '.format(self.doom_config.mod_path, 'BDoom632.pk3')
        options += '-file {0}\\{1} '.format(self.doom_config.mod_path, 'idclever-starter.pk3')
        options += '-file {0}\\{1} '.format(self.doom_config.mod_path, 'fullscrn_huds.pk3')
        return options

    def get_recording_options(self, game, episode, mission):
        return '-record MAP{0}-%datetime%.lmp '.format(str(mission.level).zfill(2))

    def get_post_game_config_commands(self, game, configuration):
        commands = []
        if configuration == 'record':
            commands.append('move *.lmp "{0}\\{1}"'.format(
                self.doom_config.demos_path,
                game.get_directory_friendly_name()))
        commands.append('cd %start%')
        commands.append('copy {0}\\{1} {2}\\{3} /Y'.format(
            self.install_path,
            self.config_name,
            self.doom_config.config_path,
            self.config_name))
        commands.append('del {0}'.format(self.config_name))
        commands.append('cd %start')
        return commands


class ZDoomSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'zdoom', 'ZDoom', 'zdoom-Chris.ini',
            'zdoom.exe', install_path, version, doom_config)


class Game(object):
    def __init__(self, name, iwad, pwad, complevel, release_date, source_ports, doom_config):
        self.name = name
        self.iwad = iwad
        self.pwad = pwad
        self.complevel = complevel
        self.release_date = release_date
        self.episodes = []
        self.source_ports = source_ports
        self.doom_config = doom_config

    def add_episode(self, episode):
        self.episodes.append(episode)

    def get_directory_friendly_name(self):
        return '{0} -- {1}'.format(self.release_date, self.name.replace(':', ' --'))

    def create_demo_directory(self):
        game_demo_path = os.path.join(
            self.doom_config.unix_demos_path,
            self.get_directory_friendly_name())
        if not os.path.exists(game_demo_path):
            os.makedirs(game_demo_path)

    def write_launch_batch_files(self):
        for source_port in self.source_ports:
            for config in source_port.get_configurations():
                if config == 'record':
                    continue
                commands = source_port.get_launch_batch_commands(self, config)
                path = self._get_launch_batch_file_path(source_port, config)
                with open(path, 'w') as f:
                    print('Writing {0}'.format(path))
                    for command in commands:
                        f.write(command + os.linesep)

    def write_map_launch_batch_files(self):
        for episode in self.episodes:
            for mission in episode.missions:
                for source_port in self.source_ports:
                    for config in source_port.get_configurations():
                        commands = source_port.get_map_launch_batch_commands(
                            self, episode, mission, config)
                        path = self._get_map_batch_file_path(episode, mission, source_port, config)
                        with open(path, 'w') as f:
                            print('Writing {0}'.format(path))
                            f.write('@echo off')
                            f.write(os.linesep)
                            f.write('echo "Playing {0} MAP{1}: E{2}M{3} - {4}"{5}'.format(
                                self.name,
                                str(mission.level).zfill(2),
                                str(episode.number).zfill(2),
                                str(mission.number).zfill(2),
                                mission.name,
                                os.linesep))
                            for command in commands:
                                f.write(command + os.linesep)

    def _get_map_batch_file_path(self, episode, mission, source_port, config):
        game_launcher_path = os.path.join(
            self.doom_config.unix_launchers_path,
            self.get_directory_friendly_name(),
            source_port.name,
            config)
        if not os.path.exists(game_launcher_path):
            os.makedirs(game_launcher_path)
        # SIGIL is a strange special case: they've called it Episode 5 of Doom,
        # but for some reason it appears in place of episode 3, meaning the warp
        # option needs to use 3 X. For that reason, the data file needs to specify
        # it as episode 3, but I still want the batch files to use episode 5.
        episode_number = episode.number if self.name != "SIGIL" else 5
        batch_file_name = 'MAP{0} -- E{1}M{2} -- {3}.bat'.format(
            str(mission.level).zfill(2),
            str(episode_number).zfill(2),
            str(mission.number).zfill(2),
            mission.get_name_for_path())
        return os.path.join(game_launcher_path, batch_file_name)

    def _get_launch_batch_file_path(self, source_port, config):
        game_launcher_path = os.path.join(
            self.doom_config.unix_launchers_path,
            self.get_directory_friendly_name(),
            source_port.name,
            config)
        if not os.path.exists(game_launcher_path):
            os.makedirs(game_launcher_path)
        return os.path.join(game_launcher_path, 'start.bat')


class Episode(object):
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.missions = []

    def add_mission(self, mission):
        self.missions.append(mission)


class Mission(object):
    def __init__(self, name, number, level, wad, is_secret_level=False):
        self.name = name
        self.number = number
        self.level = level
        self.wad = wad
        self.is_secret = is_secret_level

    def get_name_for_path(self):
        return self.name.replace('/', '').replace('!', '').replace("'", '')


class GameParser(object):
    def __init__(self, csv_path, doom_config):
        self.csv_path = csv_path
        self.doom_config = doom_config

    def parse_game(self, source_ports):
        game_data = self.get_game_data_from_csv()
        episode_boundaries = self.get_episode_boundaries(game_data)
        game = Game(
            game_data[0].game_name,
            game_data[0].iwad,
            game_data[0].pwad,
            game_data[0].complevel,
            game_data[0].release_date,
            source_ports,
            self.doom_config)
        for _, value in episode_boundaries.items():
            start = value[0]
            end = value[1]
            episode = Episode(
                game_data[start].episode_name,
                game_data[start].episode_number)
            for i in range(start, end + 1):
                is_secret_level = True if game_data[i].is_secret == 'true' else False
                episode.add_mission(Mission(
                    game_data[i].mission_name,
                    int(game_data[i].mission_number),
                    int(game_data[i].level_number),
                    game_data[i].pwad,
                    is_secret_level=is_secret_level))
            game.add_episode(episode)
        return game

    def get_game_data_from_csv(self):
        game_data = []
        with open(self.csv_path, 'r') as f:
            reader = csv.reader(f)
            GameCsvItem = namedtuple("GameCsv", next(reader))
            [game_data.append(x) for x in map(GameCsvItem._make, reader)]
        return game_data

    def get_episode_boundaries(self, game_data):
        episode_boundaries = {}
        episode = 1
        start = 0
        level_count = len(game_data)
        for index, item in enumerate(game_data):
            if int(item.episode_number) != episode:
                episode_boundaries[episode] = (start, index - 1)
                start = index
                episode += 1
            if index == level_count - 1:
                episode_boundaries[episode] = (start, index)
        return episode_boundaries


class DoomConfig(object):
    def __init__(self, windows_home_directory_path, unix_home_directory_path):
        self.windows_home_directory_path = windows_home_directory_path
        self.unix_home_directory_path = unix_home_directory_path
        self.unix_source_ports_path = os.path.join(unix_home_directory_path, 'source-ports')
        self.unix_launchers_path = os.path.join(unix_home_directory_path, 'launchers')
        self.unix_demos_path = os.path.join(unix_home_directory_path, 'demos')
        self.config_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'config')
        self.source_ports_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'source-ports')
        self.launchers_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'launchers')
        self.iwad_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'iwads')
        self.wad_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'wads')
        self.mod_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'mods')
        self.demos_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'demos')


class SourcePortBuilder(object):
    def __init__(self, doom_config):
        self.doom_config = doom_config

    def get_source_ports(self):
        source_ports = []
        source_port_directories = next(os.walk(self.doom_config.unix_source_ports_path))[1]
        port_version_pairs = [
            tuple(directory.split('-')) for directory in source_port_directories
        ]
        for port_name, version in port_version_pairs:
            install_path = '{0}\\{1}-{2}'.format(
                self.doom_config.source_ports_path,
                port_name,
                version)
            if port_name == 'crispy_doom':
                source_ports.append(
                    CrispyDoomSourcePort(install_path, version, self.doom_config))
            elif port_name == 'doom_retro':
                source_ports.append(
                    DoomRetroSourcePort(install_path, version, self.doom_config))
            elif port_name == 'gzdoom':
                source_ports.append(
                    GzDoomSourcePort(install_path, version, self.doom_config))
            elif port_name == 'zdoom':
                source_ports.append(
                    ZDoomSourcePort(install_path, version, self.doom_config))
            elif port_name == 'prboom':
                source_ports.append(
                    PrBoomSourcePort(install_path, version, self.doom_config))
            elif port_name == 'glboom':
                source_ports.append(
                    GlBoomSourcePort(install_path, version, self.doom_config))
            elif port_name == 'marshmallow_doom':
                source_ports.append(
                    MarshmallowDoomSourcePort(install_path, version, self.doom_config))
            else:
                raise ValueError('{0} not supported. Please extend to support'.format(port_name))
        return source_ports


class CliMenu(object):
    def __init__(self, game_data_path, doom_config):
        self.game_data_path = game_data_path
        self.doom_config = doom_config

    def display_source_ports(self):
        builder = SourcePortBuilder(self.doom_config)
        source_ports = builder.get_source_ports()
        print('Found the following source ports:')
        for source_port in source_ports:
            print('{0} v{1}'.format(source_port.friendly_name, source_port.version))
        print()

    def get_user_game_selection(self):
        self._display_banner()
        builder = SourcePortBuilder(self.doom_config)
        source_ports = builder.get_source_ports()
        games = self._get_game_list(source_ports)
        games_sorted_by_date = sorted(games, key=operator.attrgetter('release_date'))
        print('The following games were found:')
        for n, game in enumerate(games_sorted_by_date, start=1):
            print('{0}. {1} -- {2}'.format(n, game.release_date, game.name))
        all_option = len(games) + 1
        print('{0}. All'.format(all_option))
        print('Please select the game to generate batch files for:')
        selection = self._get_valid_input(len(games) + 1)
        if selection == all_option:
            return games_sorted_by_date
        return [games_sorted_by_date[selection - 1]]

    def _display_banner(self):
        print('=========================')
        print('Doom Batch File Generator')
        print('=========================')
        print('This utility will generate batch files for each mission in a game.')
        print('They are intended to be used as a quick way to pistol start any given mission.')
        print()

    def _get_game_list(self, source_ports):
        games = []
        os.chdir(self.game_data_path)
        for game_file in glob.glob('*.csv'):
            parser = GameParser(game_file, self.doom_config)
            games.append(parser.parse_game(source_ports))
        return games

    def _get_valid_input(self, length):
        while True:
            selection = input()
            try:
                numeric_selection = int(selection)
                if numeric_selection < 1 or numeric_selection > length:
                    raise ValueError
                return numeric_selection
            except ValueError:
                print('Please enter a value between 1 and {0}.'.format(length))


def get_doom_config():
    windows_doom_home_path = os.getenv('WINDOWS_DOOM_HOME')
    unix_doom_home_path = os.getenv('UNIX_DOOM_HOME')
    windows_usernames = next(os.walk('/c/Users'))[1]
    windows_username = next(
        username for username in windows_usernames if username not in ['Default', 'Public'])
    if not windows_doom_home_path:
        windows_doom_home_path = 'C:\\Users\\{0}\\{1}'.format(windows_username, 'doom')
    if not unix_doom_home_path:
        unix_doom_home_path = os.path.join('/c/Users', windows_username, 'doom')
    return DoomConfig(windows_doom_home_path, unix_doom_home_path)

def main():
    doom_config = get_doom_config()
    menu = CliMenu('./game-data', doom_config)
    menu.display_source_ports()
    games = menu.get_user_game_selection()
    for game in games:
        game.write_launch_batch_files()
        game.write_map_launch_batch_files()
        game.create_demo_directory()

if __name__ == '__main__':
    sys.exit(main())
