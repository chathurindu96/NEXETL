"""Execution-scoped disk-backed batch spool."""

import json
import sqlite3
import tempfile
from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


def _json_value(value):
    if isinstance(value,Decimal): return float(value)
    if isinstance(value,(date,datetime)): return value.isoformat()
    if isinstance(value,(bytes,bytearray)): return value.hex()
    raise TypeError()


class SpoolStore:
    def __init__(self,batch_size:int,max_rows:int)->None:
        handle=tempfile.NamedTemporaryFile(prefix="nexetl-run-",suffix=".sqlite3",delete=False); self.path=Path(handle.name); handle.close(); self.batch_size=batch_size; self.max_rows=max_rows; self._connection=sqlite3.connect(self.path)
        self._connection.execute("create table rows (node_id text not null, port text not null, sequence integer primary key autoincrement, payload text not null)"); self._connection.execute("create index rows_stream on rows(node_id,port,sequence)")
    def write(self,node_id:str,rows:list[dict],port:str="output")->int:
        current=self.count(node_id,port)
        if current+len(rows)>self.max_rows: raise RuntimeError("NEXETL_STATEFUL_ROW_LIMIT")
        self._connection.executemany("insert into rows(node_id,port,payload) values(?,?,?)",[(node_id,port,json.dumps(row,default=_json_value,separators=(",",":"))) for row in rows]); self._connection.commit(); return len(rows)
    def batches(self,node_id:str,port:str="output")->Iterator[list[dict]]:
        cursor=self._connection.execute("select payload from rows where node_id=? and port=? order by sequence",(node_id,port))
        while True:
            values=cursor.fetchmany(self.batch_size)
            if not values: break
            yield [json.loads(row[0]) for row in values]
    def all(self,node_id:str,port:str="output")->list[dict]: return [item for batch in self.batches(node_id,port) for item in batch]
    def count(self,node_id:str,port:str="output")->int: return int(self._connection.execute("select count(*) from rows where node_id=? and port=?",(node_id,port)).fetchone()[0])
    def close(self)->None:
        self._connection.close(); self.path.unlink(missing_ok=True)
    def __enter__(self): return self
    def __exit__(self,*_): self.close()
