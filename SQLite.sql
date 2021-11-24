-- SQLite
delete from document_part;
delete from sqlite_sequence
where name = 'document_part';
delete from proposal;
delete from sqlite_sequence
where name = 'proposal';
delete from document;
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