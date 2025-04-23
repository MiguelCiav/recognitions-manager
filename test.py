from fillpdf import fillpdfs

print()  # This will print the form fields in the PDF;
# returns a dictionary of fields
# Set the returned dictionary values a save to a variable
# For radio boxes ('Off' = not filled, 'Yes' = filled)
data_dict = {
'fecha': 'Name',
'codigo': 'LastName',
'nombre': 'Yes',
'grupo': 'Yes',
'distrito': 'Yes',
'region': 'Yes',
}

# If you want it flattened:
fillpdfs.flatten_pdf('nuevo.pdf', 'nuevo_flat.pdf')