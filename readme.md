# cubecraft-namedb
Creates database containing the names of all [cubecraft.net][cubenet] forum users.

## Installation
Requirements: `sqlite3`
```
git clone https://github.com/MagnificentSpam/cubecraft-namedb`
cd cubecraft-namedb
venv -p python3 venv
. venv/bin/activate
pip install requests-html
```

## Usage
```
python load.py [--delay <delay>] start_id end_id
```

For example to load all users (currently the latest user has the id 448140):
```
python load.py 1 448140
```
This will take a VERY long time.

## Results

The results are stored in two table with the following schemas:

`sqlite3` can be used to inspect the results.

List all usernames and old names:
```sql
select users.id, users.name, oldnames.name as oldname from users left join oldnames on users.id = oldnames.user_id;
```

Find the highest id in the database:
```sql
select id from users order by id desc limit 1;
```

Find all current names where
- the name is 6 characters long
- the last and second to last letter are the same
- the name does not contain the letters [a, i, m]
- the user has at least 150 messages
```sql
select name from users where length(name) = 6 and messages >= 150 and substr(name, 4, 1) = substr(name, 5, 1) and not name like "%a%" and not name like "%i%" and not name like "%m";
```

[cubenet]: https://cubecraft.net
