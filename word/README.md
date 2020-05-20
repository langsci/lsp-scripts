# Additional MS Word converter scripts

Some word documents use two features our converter needs help with:

 1. Fields. Fields are often used for counters, e.g. of example environments. To convert them to their evaluation in plain text so they are displayed properly in the conversion result, select the complete document and press <kbd>ctrl</kbd> <kbd>shift</kbd> <kbd>F9</kbd>.
 2. Examples in tables. Examples with glosses need alignment. Some authors use tables in Word to achieve this, but our converter can't handle them. In order to convert *all* tables in a Word document to text separated by tabstopps, open the Visual Basic for Applications window in Word using <kbd>alt</kbd> <kbd>F11</kbd>. Then import the module from `ConvertWordTablesToText.bas` and run it on the opened document.
