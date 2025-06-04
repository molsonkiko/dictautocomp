import json
from pathlib import Path
import re

from dictautocomp.trie import Trie, IgnoreCaseTrie, TrieInterface

from Npp import notepad, editor, MESSAGEBOXFLAGS
from Npp import SCINTILLANOTIFICATION
from Npp import NOTIFICATION

CURDIR = Path(__file__).parent
SETTINGS_FILE = CURDIR / 'settings.json'


def word_list_to_trie(fname: str, ignorecase: bool) -> TrieInterface:
    '''assumes a file is a whitespace-separated list of words'''
    with open(fname, 'r') as f:
        words = f.read().split()
    if ignorecase:
        return IgnoreCaseTrie(words)
    return Trie(words)
    
def is_yes(yesno):
    return yesno and yesno[0].lower() == 'y'


class AutoCompleter:
    extensions: re.Pattern
    ignorecase: bool
    min_autocomplete_length: int
    fname: str
    trie: TrieInterface

    def __init__(self,
                 extensions,  # list of strings or str
                 ignorecase: bool,
                 min_autocomplete_length: int,
                 fname: str) -> None:
        if isinstance(extensions, list):
            extensions_list = []
            for e in extensions:
                e = re.escape(e)
                if e[0] == '.':
                    extensions_list.append(e[1:])
                else:
                    extensions_list.append(e)
            self.extensions = re.compile('\\.(?:' + '|'.join(extensions_list) + ')$')
        else:
            self.extensions = re.compile(extensions)
        assert isinstance(min_autocomplete_length, int)
        self.min_autocomplete_length = min_autocomplete_length
        assert isinstance(ignorecase, bool)
        self.ignorecase = ignorecase
        try:
            self.fname = fname
            self.trie = word_list_to_trie(fname, ignorecase)
        except FileNotFoundError:
            self.trie = None
            self.fname = None

    def json(self):
        return {
            'extensions': self.extensions.pattern,
            'ignorecase': self.ignorecase,
            'min_autocomplete_length': self.min_autocomplete_length,
        }

    def __str__(self):
        return (f'AutoCompleter('
                f'extensions={self.extensions}, '
                f'ignorecase={self.ignorecase}, '
                f'min_autocomplete_length={self.min_autocomplete_length}, '
                f'fname={self.fname})')


class DAC:
    active_completer: AutoCompleter
    wordlists_to_completers: dict[str, AutoCompleter]

    def __init__(self):
        self.load_settings()
        self.active_completer = None

    def load_settings(self) -> None:
        '''The settings file will have JSON of the form
{
    "C:\\path\\to\\file\\merriam_webster_words.txt": {
        "extensions": "\\.(?:txt|md)$",
        "ignorecase": true,
        "min_autocomplete_length": 2
    },
    "C:\\another\\path\\to\\all_pythonscript_enum_members.txt": {
        "extensions": "\\.(?:py|foobar|blarzen)$",
        "ignorecase": false,
        "min_autocomplete_length": 3
    }
}
        '''
        self.wordlists_to_completers = {}
        files_not_found = False
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open() as f:
                try:
                    settings = json.load(f)
                except:
                    return
            for fname, options in settings.items():
                completer = AutoCompleter(**options, fname=fname)
                if completer.trie:
                    self.wordlists_to_completers[fname] = completer
                else:
                    # file was not found, give user option to fix it
                    files_not_found = True
                    notepad.messageBox(
                        'One of your autocompletion files no longer exists. Showing you the old settings for that file now.',
                        'Autocompletion file not found',
                        MESSAGEBOXFLAGS.OK | MESSAGEBOXFLAGS.ICONERROR)
                    extensions_pretty = ' '.join(re.findall(r'\w[\w\._-]*', options['extensions']))
                    self.add_dictionary(
                        fname=fname,
                        extensions=extensions_pretty,
                        ignorecase=options['ignorecase'],
                        min_autocomplete_length=options['min_autocomplete_length']
                    )
        else:
            # default settings if no settings file:
            # include PythonScript autocompletions as an example
            from dictautocomp.get_pythonscript_autocompletions import autocomp_file # regenerate autocompletions
            files_not_found = True
            pythonscript_filename = str((CURDIR / 'pythonscript_autocompletions.txt').absolute())
            self.wordlists_to_completers[pythonscript_filename] = AutoCompleter(['py', 'foobar'], False, 3, pythonscript_filename)
        if files_not_found:
            self.dump_settings()

    def settings_to_json_str(self) -> dict:
        return json.dumps({fname: completer.json()
                for fname, completer in self.wordlists_to_completers.items()},
            indent = 4)

    def dump_settings(self) -> None:
        with SETTINGS_FILE.open('w') as f:
            f.write(self.settings_to_json_str())

    def add_dictionary(self, fname='', extensions='', ignorecase=False, min_autocomplete_length=2) -> None:
        ignorecase_str = ['no', 'yes'][ignorecase]
        while True:
            extensions_str = ' '.join(extensions) if isinstance(extensions, list) else extensions
            options = notepad.prompt(
                'Add new autocompletion rules below',
                'Add new autocompletion rules',
                (f'word list filename: {fname}\r\n'
                f'space-separated list of extensions to autocomplete for: {extensions_str}\r\n'
                f'case-insensitive autocompletion (yes/no): {ignorecase_str}\r\n'
                f'minimum length to suggest completions: {min_autocomplete_length}\r\n'
                'remove existing autocompletions for filename: no'))
            print(options)
            if not options:
                return
            fname, exts, ignorecase, minlen, remove_existing_val = [x.split(':', 1)[1].strip()
                for x in options.split('\r\n')]
            ignorecase = is_yes(ignorecase)
            extensions = exts.split()
            minlen = int(minlen)
            remove_existing = is_yes(remove_existing_val)
            completer = AutoCompleter(extensions, ignorecase, minlen, fname)
            if remove_existing:
                if fname in self.wordlists_to_completers:
                    del self.wordlists_to_completers[fname]
                break
            if completer.trie:
                break
            # else file not found
            notepad.messageBox('Invalid filename', 'Invalid filename',
                MESSAGEBOXFLAGS.OK | MESSAGEBOXFLAGS.ICONERROR)
        if completer.trie:
            self.wordlists_to_completers[fname] = completer
        self.dump_settings()

    def bufferactivated(self, args):
        '''activate the trie associated with the current file's extension.'''
        active_fname = notepad.getCurrentFilename()
        for trie_fname, completer in self.wordlists_to_completers.items():
            if completer.extensions.search(active_fname):
                self.active_completer = completer
                return
        self.active_completer = None

    def autocomplete(self, args):
        '''if the current file's extension is associated with an autocompletion list,
        use the Trie generated for that list to find autocompletions for the current word.
        '''
        if not self.active_completer:
            return
        pos            = editor.getCurrentPos()
        word_start_pos = editor.wordStartPosition(pos, True)
        word_end_pos   = editor.wordEndPosition(pos, True)
        word_length    = word_end_pos - word_start_pos
        current_word   = editor.getRangePointer(word_start_pos, word_length).strip()
        if len(current_word) < self.active_completer.min_autocomplete_length:
            return
        completions = ' '.join(self.active_completer.trie.super_words(current_word))
        if completions:  # don't override normal autocompletions unnecessarily
            editor.autoCSetIgnoreCase(self.active_completer.ignorecase)
            editor.autoCShow(word_length, completions.encode('ansi'))

if __name__ == '__main__':
    try:
        dac
    except NameError: # will only happen the first time script is executed
        dac = DAC()
        notepad.messageBox(dac.settings_to_json_str(),
                           'Autocompletion current settings',
                           MESSAGEBOXFLAGS.ICONINFORMATION
        )
        # only add callbacks the first time the script is run
        notepad.callback(dac.bufferactivated, [NOTIFICATION.BUFFERACTIVATED, NOTIFICATION.FILERENAMED])
        editor.callback(dac.autocomplete, [SCINTILLANOTIFICATION.CHARADDED])
    dac.load_settings()
    dac.add_dictionary()
    dac.bufferactivated(None)