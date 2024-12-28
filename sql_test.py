from sql import SQL

# for k in range(30):
#     db.insert(TABLE, k=k, v=1)

# print(db.get_tables())
# print(db.has_table_privilege(TABLE, "insert"))
# print(db.get_attnames(TABLE))
# print(db.insert(TABLE, {"k":0, "v":1}))

# # Get tuple, dict, or named tuple outputs.
# q = db.query(f'select * from {TABLE}')
# q.getresult() # tuple
# q.dictresult() # list of dicts
# rows = q.namedresult() # named tuples
# rows[3].k

# print(db.query(f"select * from {TABLE}"))

s = SQL("test1", use_creds=True)
# s.insert("test2", t=54.5, rh=27.8)
s.insert("test2")
