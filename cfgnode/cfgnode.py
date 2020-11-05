# vim:ts=4:et
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from .script import Script

class ConfigNodeError(Exception):
    def __init__(self, fname, line, message):
        """
        Create a message.

        Args:
            self: (todo): write your description
            fname: (str): write your description
            line: (str): write your description
            message: (str): write your description
        """
        Exception.__init__(self, "%s:%d: %s" % (fname, line, message))
        self.message = "%s:%d: %s" % (fname, line, message)
        self.line = line

def cfg_error(self, msg):
    """
    Emit an error message.

    Args:
        self: (todo): write your description
        msg: (str): write your description
    """
    raise ConfigNodeError(self.filename, self.line, msg)

class ConfigNode:
    def __init__(self):
        """
        Initialize the values

        Args:
            self: (todo): write your description
        """
        self.values = []
        self.nodes = []
    @classmethod
    def ParseNode(cls, node, script, top = False):
        """
        Parse a script.

        Args:
            cls: (todo): write your description
            node: (todo): write your description
            script: (todo): write your description
            top: (todo): write your description
        """
        while script.tokenAvailable(True):
            token_start = script.pos
            if script.getToken(True) == None:
                break
            if script.token == "\xef\xbb\xbf":
                continue
            if script.token in (['{', '}', '='] if top else ['{', '=']):
                cfg_error(script, "unexpected " + script.token)
            if script.token == '}':
                return
            token_end = script.pos
            key = script.token
            #print(key,script.line)
            while script.tokenAvailable(True):
                script.getToken(True)
                token_end = script.pos
                line = script.line
                if script.token == '=':
                    value = ''
                    if script.tokenAvailable(False):
                        script.getLine()
                        value = script.token.strip()
                    node.values.append((key, value, line))
                    break
                elif script.token == '{':
                    new_node = ConfigNode()
                    ConfigNode.ParseNode(new_node, script, False)
                    node.nodes.append((key, new_node, line))
                    break
                else:
                    #cfg_error(script, "unexpected " + script.token)
                    key = script.text[token_start:token_end]
        if not top:
            cfg_error(script, "unexpected end of file")
    @classmethod
    def load(cls, text):
        """
        Load a list of text and returns list

        Args:
            cls: (todo): write your description
            text: (str): write your description
        """
        if not text:
            return []
        script = Script("", text, "{}=", False)
        script.error = cfg_error.__get__(script, Script)
        nodes = []
        while script.tokenAvailable(True):
            node = ConfigNode()
            ConfigNode.ParseNode(node, script, True)
            nodes.append(node)
        if len(nodes) == 1:
            return nodes[0]
        else:
            return nodes
    @classmethod
    def loadfile(cls, path):
        """
        Load a text file.

        Args:
            cls: (todo): write your description
            path: (str): write your description
        """
        bytes = open(path, "rb").read()
        text = "".join(map(lambda b: chr(b), bytes))
        return cls.load(text)
    def GetNode(self, key):
        """
        Returns the value of a node

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        for n in self.nodes:
            if n[0] == key:
                return n[1]
        return None
    def GetNodeLine(self, key):
        """
        Return a node from the given key

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        for n in self.nodes:
            if n[0] == key:
                return n[2]
        return None
    def GetNodes(self, key):
        """
        Returns a list of a given key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        nodes = []
        for n in self.nodes:
            if n[0] == key:
                nodes.append(n[1])
        return nodes
    def GetValue(self, key):
        """
        Returns the value of a key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        for v in self.values:
            if v[0] == key:
                return v[1].strip()
        return None
    def HasNode(self, key):
        """
        Returns true if the node with the given key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        for n in self.nodes:
            if n[0] == key:
                return True
        return False
    def HasValue(self, key):
        """
        Returns true if the value is in the given a key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        for v in self.values:
            if v[0] == key:
                return True
        return False
    def GetValueLine(self, key):
        """
        Returns the value of a given key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        for v in self.values:
            if v[0] == key:
                return v[2]
        return None
    def GetValues(self, key):
        """
        Get a list of a given value.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        values = []
        for v in self.values:
            if v[0] == key:
                values.append(v[1])
        return values
    def AddNode(self, key, node):
        """
        Add a node.

        Args:
            self: (todo): write your description
            key: (str): write your description
            node: (todo): write your description
        """
        self.nodes.append((key, node))
        return node
    def AddNewNode (self, key):
        """
        Add a new node

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        node = ConfigNode ()
        self.nodes.append((key, node))
        return node

    def AddValue(self, key, value):
        """
        Add an entry to the list.

        Args:
            self: (todo): write your description
            key: (str): write your description
            value: (todo): write your description
        """
        self.values.append((key, value))
    def SetValue(self, key, value):
        """
        Returns the value of a given key.

        Args:
            self: (todo): write your description
            key: (str): write your description
            value: (todo): write your description
        """
        for i in range(len(self.values)):
            if self.values[i][0] == key:
                self.values[i] = key, value, 0
                return
        self.AddValue(key, value)
    def ToString(self, level = 0):
        """
        Convert the node to text.

        Args:
            self: (todo): write your description
            level: (int): write your description
        """
        extra = 0
        if level >= 0:
            extra = 2
        text=[None] * (len(self.values) + len(self.nodes) + extra)
        index = 0
        if level >= 0:
            text[index] = "{\n"
            index += 1
        for val in self.values:
            text[index] = "%s%s = %s\n" % ("    " * (level + 1), val[0], val[1])
            index += 1
        for node in self.nodes:
            ntext = node[1].ToString(level + 1)
            text[index] = "%s%s %s\n" % ("    " * (level + 1), node[0], ntext)
            index += 1
        if level >= 0:
            text[index] = "%s}\n" % ("    " * (level))
            index += 1
        return "".join(text)

if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        text = open(arg, "rt").read()
        try:
            node = ConfigNode.load(text)
        except ConfigNodeError as e:
            print(arg+e.message)
