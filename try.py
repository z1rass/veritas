import pickledb

db = pickledb.load('try.db', True)

db.set('1', {'username': 'Matvii'})
db.set('2', {'username': 'Joe'})

keys = db.getall()

for i in keys:
    post = db.get(i)
    if post['username'] == 'Matvii':
        print(post["username"])
