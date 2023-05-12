from flask import Flask, request, render_template, session
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    "host=db dbname=postgres user=postgres password=postgres",
    cursor_factory=RealDictCursor)
app = Flask(__name__)
app.secret_key = 'muafdadsfasdfa'


@app.route("/")
def hello_world():
    name = request.args.get("name", "World")
    return f"<p>Hello, {name}!</p>"

@app.route("/sets")
def fetch_sets():

    def sanity(value, valid_values, default):
        if(value not in valid_values):
            return default
        else:
            return value
    
    sorts = {'set_num','set_name','theme_name','year','part_count'}
    limits = {10,50,100}
        
    sort_dir = sanity(request.args.get("sort_dir","asc"),{'asc','desc'},'asc')
    set_name = request.args.get("set_name","")
    theme_name = request.args.get("theme_name","")
    min_part_count = request.args.get("min_part_count","0")
    max_part_count = request.args.get("max_part_count","10000")
    limit = sanity(int(request.args.get("limit","50")),limits,50)
    sort_by = sanity(request.args.get("sort_by","set_name"),sorts,'set_name')
    offset = int(request.args.get("offset","0"))
    sort_byp = sanity(request.args.get("sort_byp",""),sorts,'')

    toffset = offset
    offset = (offset - 1) * limit if offset > 0 else 0

    
    if sort_by == sort_byp:
        if sort_dir == 'asc':
            sort_dir = 'desc'
        else:
            sort_dir = 'asc'
    else:
        sort_dir = 'asc'

    def arrow(name):
        if request.args.get('sort_by','set_name') == name:
            if request.args.get('sort_dir','asc') == 'asc':
                return '▲' 
            else:
                return '▼'
        else:
            return ''
            
    params = [sort_dir, set_name, theme_name, min_part_count, max_part_count, limit,toffset]
    names = ["sort_dir","set_name","theme_name","min_part_count","max_part_count","limit"]

    link = f'http://127.0.0.1:5000/sets?set_name={set_name}&theme_name={theme_name}&min_part_count={min_part_count}&max_part_count={max_part_count}&limit={limit}&sort_dir={sort_dir}&offset={toffset}'

    query = f"""select set.set_num as set_num, set.name as set_name, set.year as year, theme.name as theme_name, count(set.num_parts) as part_count
                from set
                join theme on set.theme_id= theme.id
                join inventory on set.set_num = inventory.set_num 
                join inventory_part on inventory.id = inventory_part.inventory_id
                where set.name ilike %(set_name)s and theme.name ilike %(theme_name)s
                group by set.set_num, set_name, year, theme.name
                having count(set.num_parts) > %(min_part_count)s and count(set.num_parts) < %(max_part_count)s
                order by {sort_by} {sort_dir}
                """
    with conn.cursor() as cur:
        cur.execute(f"""
                        {query} limit %(limit)s 
                        offset %(offset)s
                    """,
                    {
                    "set_name": f'%{set_name}%',
                    "theme_name": f"%{theme_name}%",
                    "min_part_count": min_part_count,
                    "max_part_count": max_part_count,
                    "limit": limit,
                    "offset": offset
                })        
        result = list(cur.fetchall())
    with conn.cursor() as cur:
        cur.execute(f"select count(*) as num from ({query}) as sub",
                    {
                    "set_name": f'%{set_name}%',
                    "theme_name": f"%{theme_name}%",
                    "min_part_count": min_part_count,
                    "max_part_count": max_part_count
                })
        num = cur.fetchone()["num"]
    pages = num // limit + 1
    return render_template("sets.html",rows=result,nums=num,link=link,pages=pages,params=params,names=names,sort_by=sort_by)