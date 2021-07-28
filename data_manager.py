import typing
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

PLOT_DATA_POINTS = 1000


@dataclass
class PlotSeriesData:
    name: str
    data: deque


class PlotGraphData(QObject):
    data_updated = pyqtSignal()

    def __init__(self, name: str, parent: typing.Optional['QObject'] = ...) -> None:
        super().__init__(parent)
        self.name: str = name
        self.series: [PlotSeriesData] = []


@dataclass
class PlotChannelData:
    name: str
    pretty_name: str
    graphs: [PlotGraphData] = field(default_factory=list)
    total_series_count: int = 0


@dataclass
class CommandArgument:
    name: str
    optional: bool
    options: [str] = field(default_factory=list)


class ChannelArgumentType(Enum):
    NONE = 0
    CHANNEL = 1
    ALL = 2
    CHANNEL_ALL = 3


class Command(QObject):
    arg_values_updated = pyqtSignal(list)

    def __init__(self, name: str, pretty_name: str, channel: ChannelArgumentType, parent=None) -> None:
        super().__init__(parent)
        self.name: str = name
        self.pretty_name: str = pretty_name
        self.channel: ChannelArgumentType = channel
        self.has_optional_arg: bool = False
        self.args: [CommandArgument] = []


@dataclass
class GroupData:
    name: str
    channels: [PlotChannelData] = field(default_factory=list)
    commands: {str: Command} = field(default_factory=dict)  # name -> Command


class DataManager(QObject):
    user_message = pyqtSignal(str)
    send_command = pyqtSignal(str)

    group_added = pyqtSignal(GroupData)  # group is completed when this signal is emitted
    normal_commands_added = pyqtSignal(list)  # list of normal commands

    def __init__(self) -> None:
        super(DataManager, self).__init__()
        self.groups: {str: GroupData} = {}  # group abbr -> group data
        self.help_requested: bool = False
        self.pending_usages: {str: [str]} = {}  # group addr -> [command]

    def reload(self) -> None:

        self.groups.clear()
        self.pending_usages.clear()

        # Send help command to query for available commands
        self.help_requested = True
        self.send_command.emit("help")
        # Wait for process_line to handle

    @pyqtSlot(str)
    def process_line(self, line: str) -> bool:
        """
        Process a line from connection.
        :return: True if the line should be printed to terminal (not internal data).
        """
        if len(line) < 3:
            return True

        if line[0] == '_':
            group_abbr = line[1]

            if line[2] == ':':  # define new groups
                self.groups[group_abbr] = GroupData(name=line[3:])
                if group_abbr not in self.pending_usages.keys():
                    self.user_message.emit(f"Unexpected group {line}")
                    return False
                self.pending_usages[group_abbr].remove("_" + group_abbr)  # clear the group info command

            else:

                group: GroupData = self.groups.get(group_abbr)
                if group is None:
                    self.user_message.emit(f"Unexpected group: {line}")
                    return False

                if line[2] == '/':  # add a new channel

                    p = line[3:].split(":")
                    if len(p) != 2:
                        self.user_message.emit(f"Invalid channel definition: {line[3:]}")
                        return False

                    channel = PlotChannelData(name=p[0], pretty_name=p[0].replace('_', ' '))

                    # Process graphs
                    for graph_def in p[1].split(' '):
                        i = graph_def.find('{')
                        if not graph_def.endswith("}") or i == -1:
                            self.user_message.emit(f"Invalid graph definition: {graph_def}")
                            return False

                        graph = PlotGraphData(name=graph_def[:i], parent=self)

                        # Process series
                        for series_name in graph_def[i + 1:-1].split(','):
                            graph.series.append(PlotSeriesData(name=series_name, data=deque([0] * PLOT_DATA_POINTS,
                                                                                            maxlen=PLOT_DATA_POINTS)))
                            channel.total_series_count += 1

                        channel.graphs.append(graph)

                    group.channels.append(channel)

                else:  # feedback or set arguments

                    p = line.split(' ')
                    if p[0][2:].isnumeric():  # feedback
                        channel_id = int(p[0][2:])
                        if channel_id >= len(group.channels):
                            self.user_message.emit(f"Motor id out of bound: {line}")
                            return False
                        channel = group.channels[channel_id]
                        if len(p) - 1 != channel.total_series_count:
                            self.user_message.emit(f"Expecting {channel.total_series_count} values: {line}")
                            return False
                        try:
                            vals = [float(s) for s in p[1:]]
                            i = 0
                            for graph in channel.graphs:
                                for series in graph.series:
                                    series.data.append(vals[i])
                                    i += 1
                                graph.data_updated.emit()
                        except ValueError:
                            self.user_message.emit(f"Invalid value(s): {line}")
                            return False

                    else:  # command getter
                        command = group.commands.get(p[0])
                        if command is None:
                            self.user_message.emit(f"Unknown command: {line}")
                            return False
                        if len(p) - 1 != len(command.args):
                            self.user_message.emit(f"Expecting {len(command.args)} arguments: {line}")
                            return False
                        command.arg_values_updated.emit(p[1:])

        else:  # line not starts with '_'

            if line.startswith("Usage: "):
                line = line[len("Usage: "):]
                group_abbr = line[1]
                if group_abbr not in self.pending_usages.keys():
                    self.user_message.emit(f"Unknown group for usage {line}")
                    return False
                p = line.split(' ')
                if p[0] not in self.pending_usages[group_abbr]:
                    self.user_message.emit(f"Unexpected command usage {line}")
                    return False
                if len(p) < 2:
                    self.user_message.emit(f"Invalid usage {line}")
                    return False

                group: GroupData = self.groups[group_abbr]
                channel: ChannelArgumentType = ChannelArgumentType.NONE
                if p[1] == "Channel":
                    channel = ChannelArgumentType.CHANNEL
                elif p[1] == "All":
                    channel = ChannelArgumentType.ALL
                elif p[1] == "Channel/All":
                    channel = ChannelArgumentType.CHANNEL_ALL
                command = Command(name=p[0], pretty_name=p[0][3:], channel=channel, parent=self)

                # Process arguments
                for arg_def in p[(1 if channel == ChannelArgumentType.NONE else 2):]:
                    if arg_def.startswith('[') and arg_def.endswith(']'):
                        arg_optional = True
                        arg_def = arg_def[1:-1]
                        command.has_optional_arg = True
                    else:
                        arg_optional = False
                    if (i := arg_def.find('{')) != -1 and arg_def.endswith('}'):
                        arg_name = arg_def[:i]
                        arg_options = arg_def[i + 1:-1].split(',')
                    else:
                        arg_name = arg_def
                        arg_options = []
                    command.args.append(CommandArgument(name=arg_name, optional=arg_optional, options=arg_options))

                group.commands[command.name] = command

                self.pending_usages[group_abbr].remove(p[0])
                if len(self.pending_usages[group_abbr]) == 0:
                    self.group_added.emit(group)
                return False
            elif line.startswith("Commands: "):

                if not self.help_requested:
                    return True

                self.help_requested = False
                line = line[len("Commands: "):]
                normal_commands = []
                commands_to_send = []  # setup pending_usages completely before sending commands
                for command in line.split(' '):
                    if not command.startswith('_'):
                        normal_commands.append(command)
                    else:
                        if len(command) < 2:
                            self.user_message.emit(f"Invalid internal command name: {command}")
                        else:
                            group_abbr = command[1]
                            if group_abbr not in self.pending_usages.keys():
                                self.pending_usages[group_abbr] = []
                            self.pending_usages[group_abbr].append(command)
                            if len(command) == 2:  # group info command such as _g
                                commands_to_send.append(command)
                            else:  # group command such as _g_pid
                                commands_to_send.append(command + " ?")
                            # Add group and command data as these commands returns

                self.normal_commands_added.emit(normal_commands)
                for c in commands_to_send:
                    self.send_command.emit(c)
                return False

            else:  # not usage or help
                return True

    def clear_data(self):
        for group in self.groups.values():
            for channel in group.channels:
                for graph in channel.graphs:
                    for series in graph.series:
                        series.data.clear()
                    graph.data_updated.emit()


def _test() -> (DataManager, [GroupData]):
    groups = []
    m = DataManager()

    def handle_group_added(group):
        print("Group added: ")
        print(group)
        groups.append(group)

    def handle_normal_commands_added(commands):
        print("Normal commands added: ")
        print(commands)

    def handle_user_message(message):
        print("!", message)

    def reply_line(line: str):
        print("<", line)
        m.process_line(line)

    def handle_send_command(command: str):
        print(">", command)
        if command == "help":
            reply_line("hello stats _s _s_enable_fb _s_pid _g _g_enable_fb")
        elif command == "_s":
            reply_line("_s:Shoot")
            reply_line("_s/Bullet:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
            reply_line("_s/FW_Left:Velocity{Target,Actual} Current{Target,Actual}")
            reply_line("_s/FW_Right:Velocity{Target,Actual} Current{Target,Actual}")
        elif command == "_s_enable_fb ?":
            reply_line("Usage: _s_enable_fb Channel/All [Feedback{Disabled,Enabled}]")
        elif command == "_s_pid ?":
            reply_line("Usage: _s_pid Channel PID{A2V,V2I} [kp] [ki] [kd] [i_limit] [out_limit]")
        elif command == "_g":
            reply_line("_g:Gimbal")
            reply_line("_g/Yaw:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
            reply_line("_g/Pitch:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
            reply_line("_g/Sub_Pitch:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
        elif command == "_g_enable_fb ?":
            reply_line("Usage: _g_enable_fb Channel/All")
        else:
            print("?", f"Unknown command {command}")

    m.user_message.connect(handle_user_message)
    m.send_command.connect(handle_send_command)
    m.group_added.connect(handle_group_added)
    m.normal_commands_added.connect(handle_normal_commands_added)
    m.reload()
    return m, groups


if __name__ == '__main__':
    _test()
