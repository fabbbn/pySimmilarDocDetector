-- SQLite
delete from case_bases;
delete from sqlite_sequence
where name = 'case_bases';
delete from document_part;
-- where document_part_id in (21, 22, 23, 24, 25);
delete from sqlite_sequence
where name = 'document_part';
-- SELECT dp.document_part_name as doc_part_name,
--     p.proposal_title as doc_title,
--     dp.document_part_id as doc_part_id,
--     d.document_id as doc_id,
--     d.document_filename as doc_filename
-- FROM document as d
--     INNER JOIN proposal as p ON d.document_id = p.proposal_doc_id
--     INNER JOIN document_part as dp ON dp.doc_id = d.document_id;
delete from proposal;
-- where proposal_id = 3;
delete from document;
-- where document_id = 3;
-- delete from proposal
-- where proposal_doc_id = 5;
delete from sqlite_sequence
where name = 'proposal';
-- delete from document
-- where document_id = 5;
delete from sqlite_sequence
where name = 'document';
delete from bag_of_words;
-- INSERT INTO case_bases (
--         doc_id,
--         doc_part_name,
--         sim_doc_id,
--         sim_doc_part_name,
--         cos_sim_value,
--         config_used
--     )
-- VALUES (
--         (
--             SELECT doc_id
--             FROM document_part
--             WHERE document_part_id = :doc_part_id
--         ),
--         (
--             SELECT document_part_name
--             FROM document_part
--             WHERE document_part_id = :doc_part_id
--         ),
--         (
--             SELECT doc_id
--             FROM document_part
--             WHERE document_part_id = :sim_doc_part_id
--         ),
--         (
--             SELECT document_part_name
--             FROM document_part
--             WHERE document_part_id = :sim_doc_part_id
--         ),
--         :cos_sim_value,
--         :config
--     );
-- ALTER TABLE case_bases ADD COLUMN config_used varchar not null default "manning";
-- ALTER TABLE case_bases RENAME COLUMN congig_used TO config_used;
-- delete from sqlite_sequence
-- where name = 'bag_of_words';
-- insert
--     or replace into bag_of_words (token, frequency, document_occurence)
-- values ("11", 5, 1) on conflict(token) do
-- update
-- set frequency = (
--         select frequency
--         from bag_of_words
--         where token = excluded.token
--     ) + excluded.frequency,
--     document_occurence = (
--         select document_occurence
--         from bag_of_words
--         where token = excluded.token
--     ) + excluded.document_occurence;
-- -- insert into bag_of_words (token, frequency, document_occuresnce) values ("broken", 5, 2);
-- ALTER TABLE document_part DELETE document_part_filename;
-- alter table case_bases drop COLUMN doc_part_name varchar;