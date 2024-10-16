Simple Python SDK for fetching files from Veeva Clinical


# Usage

```
from classes.veeva_clinical import VeevaClinical

client = VeevaClinical('<veeva clinical dns>','<user name>','<password>')

#list all files, returns a VeevaDocument object
documents = client.list_all_files()


#download each file, save to disk
for document in documents:
  with open(document.name,'wb') as f:
    f.write(document.download())
```
