# Introduction:
There are few algorithms that can solve this problem. I tested two:
1. Adjacent List done recursively - I have tested it locally, but it has poor performance. Each child would need separate query, what makes this approach not-scalable for big amounts of data especially deep ones.
```python
   def get_descendants(assembly: Assembly) -> Iterable[Assembly]:
        queryset = Assembly.objects.filter(parent=assembly)
        results = chain(queryset)
        for child in queryset:
            results = chain(results, get_descendants(child)) # each child requires query
        return results
```
 
3. Materialized Path Tree. This method is about adding some structured path to each element of a tree, eg.:<br/>
    0th level deep:      (headphones) will get         `path=0001`:<br/>
     1st level deep:     (Assembled headmount)         `path=00010001`:<br/>
      2st level deep:    (covered headmount)           `path=000100010001`:<br/>
       3rd level deep:   (plastic structure headmount) `path=0001000100010001`:<br/>
       3rd level deep:   (solid foa)                   `path=0001000100010002`:<br/>
       3rd level deep:   (leather rectange)            `path=0001000100010003`:<br/>
      2nd level deep:    (assembled arm)               `path=000100010002`:<br/>
       3rd level deep:   (plastic connector)           `path=0001000100020001`:<br/>
       3rd level deep:   (slider metal)                `path=0001000100020002`:<br/>
Such approach will require only one SQL query from us to get the whole tree, that is:
`SELECT * FROM Assembly WHERE path LIKE '0001%`
or in Django:
`tree = Assembly.objects.filter(path__startswith=assembly.path)`

_________________________________________________________________________________________
# RUN APP
## Prerequisites:
- docker and docker-compose binaries installed

### To run project:
`docker-compose up --build`

### To create superuser:
`docker-compose exec web python manage.py createsuperuser` (in different terminal)

Files that have been tested are located in: `ravacan/_files/` directory.

### OpenAPI schema:
`http://127.0.0.1:8000/api/schema/`
### Other endpoints:
- `http://127.0.0.1:8000/api/bom/file/validate/`
- `http://127.0.0.1:8000/api/bom/file/upload/`
- `http://127.0.0.1:8000/api/bom/items/`
- `http://127.0.0.1:8000/api/bom/items/<id>/`
- `http://127.0.0.1:8000/admin/` - nice looking view of Assemblies


--------------------------------------------------------------
## TODO PROD:
- add abstraction layer on top of upload file feature (probably in future there will be many formats of files to upload)
- add Celery support for uploading
- add more unittests
- run inside Kubernetes
