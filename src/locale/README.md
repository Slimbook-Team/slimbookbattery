# Translations.

# How to create a new translation?
1. Create the new language folder with the correct language nomenclature, then create a new folder inside and name it LC_MESSAGES.
2. Move the files '*.template.po' (which are outside the language folders) to the folder named LC_MESSAGES in your folder.
3. Edit those files with your translations.
4. Upload the new folder to this repository route.

Tip: You can use the existent folders as a guide to translate *.po files in your folder.

# How to edit an existent translation?
1. Edit .po files in the language folder.
2. Upload the new folder to this repository route.

(We will compile them to .mo, although you can try to do it by executing 'bash compila_mo.sh' inside the locale folder)
