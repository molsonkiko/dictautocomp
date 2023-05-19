# Efficient autocompletion from very large word lists in Notepad++

Scintilla, the editing component powering Notepad++, uses an autocompletion algorithm that does not scale well to very large predefined lists of words. This is a problem if, for example, you want to autocomplete any word from the Merriam-Webster English Dictionary, which contains tens of thousands of words.

This plugin uses the [trie data structure](https://en.wikipedia.org/wiki/Trie) and a case-insensitive trie variant to store large numbers of words in a way that is amenable to autocompletion, albeit *rather memory-intensive.*

In addition, you can define different autocompletion lists for different file types. To get you started, a [list of autocompletions for the PythonScript plugin](/pythonscript_autocompletions.txt) is included in this repository.

![example of autocompletion with this plugin](/example.PNG)

This plugin requires [PythonScript](https://github.com/bruderstein/PythonScript/releases) version 3 or higher.