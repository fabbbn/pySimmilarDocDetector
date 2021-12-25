-- SQLite
-- alter table case_bases add column retrieved integer not null default 0;
-- alter table case_bases add column reused integer not null default 0;
-- alter TABLE case_bases add column exc_time real not null DEFAULT o;
-- SELECT *
-- from case_bases
-- where doc_id >=51 and doc_id<=60;
select 
    c.doc_id as doc_id, 
    p.proposal_title as doc_title,
    c.doc_part_name as doc_part,
    c.sim_doc_id as sim_doc_id, 
    c.sim_doc_part_name as sim_doc_part, 
    pr.proposal_title as sim_doc_title,
    sum(c.reused) as tot_reused, 
    sum(c.retrieved) as tot_retrieved, 
    max(c.cos_sim_value) as highest_cosine, 
    c.config_used as config_used,  
    c.exc_time 
from 
    case_bases as c 
    inner join proposal as p on c.doc_id=p.proposal_doc_id
    inner join proposal as pr on c.sim_doc_id=pr.proposal_doc_id
where doc_id>50 group by c.doc_id, c.doc_part_name,c.config_used order by c.doc_id