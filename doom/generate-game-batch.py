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

    def get_launch_commands(self, game, episode, mission):
        commands = []
        commands.append('set start=%cd%')
        commands.append('copy {0}\\{1} {2}\\{3} /Y'.format(
            self.doom_config.config_path,
            self.config_name,
            self.install_path,
            self.config_name))
        commands.append('cd {0}'.format(self.install_path))
        launch_command = '{0} '.format(self.exe_name)
        launch_command += self.get_game_options(game)
        launch_command += self.get_misc_options()
        launch_command += self.get_skill_option()
        launch_command += self.get_warp_option(game, episode, mission)
        commands.append(launch_command)
        commands.append('del {0}'.format(self.config_name))
        commands.append('cd %start%')
        return commands

    def get_game_options(self, game):
        options = '-config {0} '.format(self.config_name)
        options += '-iwad {0}\\{1} '.format(self.doom_config.iwad_path, game.iwad)
        if game.wad:
            options += '-file {0}\\{1} '.format(self.doom_config.wad_path, game.wad)
        return options

    def get_misc_options(self):
        return '-nomusic -fullscreen '

    def get_skill_option(self):
        return '-skill 4 '

    def get_warp_option(self, game, episode, mission):
        if game.iwad == 'DOOM2.WAD':
            return '-warp {0}'.format(str(mission.level).zfill(2))
        elif game.iwad == 'DOOM.WAD':
            return '-warp {0} {1}'.format(episode.number, mission.number)
        raise ValueError('iwad {0} not supported yet'.format(game.iwad))


class CrispyDoomSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'crispy', 'Crispy Doom', 'crispy-doom.cfg',
            'crispy-doom.exe', install_path, version, doom_config)


class DoomRetroSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'retro', 'Doom Retro', 'doomretro.cfg',
            'doomretro.exe', install_path, version, doom_config)

    def get_misc_options(self):
        return '-pistolstart -nomusic '

    def get_warp_option(self, game, episode, mission):
        return '-warp E{0}M{1}'.format(episode.number, mission.number)


class BoomSourcePort(SourcePort):
    def get_game_options(self, game):
        options = '-iwad {0}\\{1} '.format(self.doom_config.iwad_path, game.iwad)
        if game.wad:
            options += '-file {0} '.format(game.wad)
        options += '-complevel {0} '.format(game.complevel)
        return options

    def get_misc_options(self):
        return '-nowindow -noaccel -nomusic '


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


class ZDoomSourcePort(SourcePort):
    def __init__(self, install_path, version, doom_config):
        SourcePort.__init__(
            self, 'zdoom', 'ZDoom', 'zdoom-Chris.ini',
            'zdoom.exe', install_path, version, doom_config)


class Game(object):
    def __init__(self, name, iwad, wad, complevel, release_date, source_ports, doom_config):
        self.name = name
        self.iwad = iwad
        self.wad = wad
        self.complevel = complevel
        self.release_date = release_date
        self.episodes = []
        self.source_ports = source_ports
        self.doom_config = doom_config

    def add_episode(self, episode):
        self.episodes.append(episode)

    def write_batch_files(self):
        for episode in self.episodes:
            for mission in episode.missions:
                for source_port in self.source_ports:
                    commands = source_port.get_launch_commands(self, episode, mission)
                    path = self._get_batch_file_path(episode, mission, source_port)
                    with open(path, 'w') as f:
                        print('Writing {0}'.format(path))
                        f.write('@echo off')
                        f.write(os.linesep)
                        f.write('echo "Playing {0} E{1}M{2}: {3}"{4}'.format(
                            self.name,
                            str(episode.number).zfill(2),
                            str(mission.number).zfill(2),
                            mission.name,
                            os.linesep))
                        for command in commands:
                            f.write(command + os.linesep)

    def _get_batch_file_path(self, episode, mission, source_port):
        game_launcher_path = os.path.join(
            self.doom_config.unix_launchers_path,
            '{0} -- {1}'.format(self.release_date, self.name.replace(':', ' --')),
            source_port.name)
        if not os.path.exists(game_launcher_path):
            os.makedirs(game_launcher_path)
        batch_file_name = 'MAP{0} -- E{1}M{2} -- {3}.bat'.format(
            str(mission.level).zfill(2),
            str(episode.number).zfill(2),
            str(mission.number).zfill(2),
            mission.name)
        return os.path.join(game_launcher_path, batch_file_name)


class Episode(object):
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.missions = []

    def add_mission(self, mission):
        self.missions.append(mission)


class Mission(object):
    def __init__(self, name, number, level, is_secret_level=False):
        self.name = name
        self.number = number
        self.level = level
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
        self.config_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'config')
        self.source_ports_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'source-ports')
        self.launchers_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'launchers')
        self.iwad_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'iwad')
        self.wad_path = '{0}\\{1}'.format(self.windows_home_directory_path, 'wad')


class SourcePortBuilder(object):
    def __init__(self, doom_config):
        self.doom_config = doom_config

    def get_source_ports(self):
        source_ports = []
        source_port_directories = next(os.walk(self.doom_config.unix_source_ports_path))[1]
        port_version_pairs = [
            tuple(directory.split('-')) for directory in source_port_directories
        ]
        for port_version_pair in port_version_pairs:
            port_name, version = port_version_pair
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
        print('Please select the game to generate batch files for:')
        selection = self._get_valid_input(len(games))
        return games[selection - 1]

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
    windows_usernames = next(os.walk('/mnt/c/Users'))[1]
    windows_username = next(
        username for username in windows_usernames if username not in ['Default', 'Public'])
    if not windows_doom_home_path:
        windows_doom_home_path = 'C:\\Users\\{0}\\{1}'.format(windows_username, 'doom')
    if not unix_doom_home_path:
        unix_doom_home_path = os.path.join('/mnt/c/Users', windows_username, 'doom')
    return DoomConfig(windows_doom_home_path, unix_doom_home_path)

def main():
    doom_config = get_doom_config()
    menu = CliMenu('./game-data', doom_config)
    menu.display_source_ports()
    game = menu.get_user_game_selection()
    game.write_batch_files()

if __name__ == '__main__':
    sys.exit(main())
