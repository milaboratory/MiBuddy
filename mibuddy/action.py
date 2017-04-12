from subprocess import Popen


class Command(object):
    def execute(self):
        """
        Runs the command
        :return: started process or None
        """
        raise NotImplementedError("Should have implemented get_commands(self) method.")


class ShellCommand(Command):
    def __init__(self, cmd, cwd):
        self.cmd = cmd
        self.cwd = cwd

    def execute(self):
        return Popen(self.cmd, cwd=self.cwd)


class CreateFile(Command):
    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content

    def execute(self):
        with open(self.file_path, "w") as f:
            f.write(self.content)
        return None


class AbstractAction(object):
    def get_commands(self):
        """
        Returns nested list/tuple of commands  
        """
        raise NotImplementedError("Should have implemented get_commands(self) method.")
