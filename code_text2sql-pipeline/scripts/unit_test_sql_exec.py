from utils.sql_exec import query_db

cmd="SELECT first_name ,  last_name FROM players ORDER BY birth_date"
# cmd="select t1.last_name , t1.first_name from players as T1 join matches as T2 on T1.player_id = T2.winner_id order by t2.winner_age asc"
db_name="wta_1"

print(query_db(db_name=db_name, db_path='../utils/database-spider/database-dev', cmd=cmd))