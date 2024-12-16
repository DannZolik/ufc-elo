SELECT f.id, w.name as 'Winner name', l.name as 'Loser name', f.method, f.winner_before_elo, f.winner_after_elo, f.loser_before_elo, f.loser_after_elo FROM `fights` as f 
inner join fighters as w on f.winner_id=w.id
inner join fighters as l on f.loser_id=l.id

order by f.id asc;