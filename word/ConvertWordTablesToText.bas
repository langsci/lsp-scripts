Attribute VB_Name = "Modul1"
Sub ConvertTablesToText()
Dim table As table
For Each table In ActiveDocument.Tables
table.ConvertToText (wdSeparateByTabs)
Next table
Set table = Nothing
End Sub
