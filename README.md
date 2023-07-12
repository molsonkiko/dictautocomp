# Efficient autocompletion from very large word lists in Notepad++

Scintilla, the editing component powering Notepad++, uses an autocompletion algorithm that does not scale well to very large predefined lists of words. This is a problem if, for example, you want to autocomplete any word from the Merriam-Webster English Dictionary, which contains tens of thousands of words.

This plugin uses the [trie data structure](https://en.wikipedia.org/wiki/Trie) and a case-insensitive trie variant to store large numbers of words in a way that is amenable to autocompletion, albeit *rather memory-intensive.*

In addition, you can define different autocompletion lists for different file types. To get you started, a [list of autocompletions for the PythonScript plugin](/pythonscript_autocompletions.txt) is included in this repository.

![example of autocompletion with this plugin](/example.PNG)

## Installation

1. Download version 3 or higher of the [PythonScript plugin](https://github.com/bruderstein/PythonScript/releases).
2. [Download the code](https://github.com/molsonkiko/dictautocomp/raw/main/dictautocomp.zip) of this repo.
3. Unzip the downloaded code into a folder named `dictautocomp`.
4. Drop the new `dictautocomp` folder in `%Appdata%\Roaming\Notepad++\plugins\config\PythonScript\scripts`
5. Go to `Plugins->Python Script->Configuration...` from the main menu, find `dictautocomp\dictautocomp.py` from the list as shown in the below image, select `User Scripts`, and click the leftmost `Add` button.
    ![Add dictautocomp to PythonScript plugin menu](/add_dictautocomp_to_plugin_menu.PNG)
6. At this point `dictautocomp` will be on the short list of PythonScript scripts, and if desired you can add a keyboard shortcut from `Macro->Modify Shortcut/Delete Macro...` from the main menu, as shown in the below image. *NOTE: you will need to restart Notepad++ for dictautocomp to appear on this list.*
    ![Add keyboard shortcut for dictautocomp](/add_dictautocomp_keyboard_shortcut.PNG)
    
## Using Dictionary Autocompletion

1. Run `Plugins->Python Script->dictautocomp`
2. It will pop up a dialog showing you the current configuration; you can hit __OK__ here
3. It will pop up a second dialog: if you want to add a new dictionary or remove a dictionary in the current config, fill out the form and hit __OK__; otherwise, hit __Cancel__ to *not* add another dictionary
4. If you are in a file whose extension that matches the "extensions" field from either the "current configuration" from step 2 *or* the new dictionary configuration you added in step 3, then as you type, the auto-completion will include the words from the dictionary
5. This auto-completion will continue until you exit Notepad++. The next time you run the application, you will have to run this script again.