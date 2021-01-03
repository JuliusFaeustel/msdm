-- Profiling
SET @@profiling = 0;
SET @@profiling_history_size = 0;
SET @@profiling_history_size = 1000; 
SET @@profiling = 1;
show profiles;

SELECT Count(Query_ID) FROM INFORMATION_SCHEMA.PROFILING where State = 'end';
SELECT * FROM INFORMATION_SCHEMA.PROFILING where State = 'end';

INSERT INTO LINIE VALUE ('9');

SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING WHERE Query_ID = 10;

SELECT * FROM INFORMATION_SCHEMA.PROFILING ;

-- DB-Größe
SELECT table_schema,
sum( data_length ) / 1024 / 1024 "Database Size in MB"
FROM information_schema.TABLES WHERE table_schema="project_2";

SELECT * FROM information_schema.TABLES WHERE table_schema="project_2";


-- Buffer Size berechnen

SELECT CEILING(Total_InnoDB_Bytes*1.6/POWER(1024,3)) RIBPS FROM
(SELECT SUM(data_length+index_length) Total_InnoDB_Bytes
FROM information_schema.tables WHERE engine='InnoDB') A;

SELECT CONCAT(CEILING(RIBPS/POWER(1024,pw)),SUBSTR(' KMGT',pw+1,1))
Recommended_InnoDB_Buffer_Pool_Size FROM
(
    SELECT RIBPS,FLOOR(LOG(RIBPS)/LOG(1024)) pw
    FROM
    (
        SELECT SUM(data_length+index_length)*1.1*growth RIBPS
        FROM information_schema.tables AAA,
        (SELECT 1.25 growth) BBB
        WHERE ENGINE='InnoDB'
    ) AA
) A;

-- Index Größe Server
select
page_type as Page_Type,
sum(data_size)/1024/1024 as Size_in_MB
from information_schema.innodb_buffer_page
group by page_type
order by Size_in_MB desc;

-- Indizes einsehen
select sum(Size_in_MB) from (
select
table_name as Table_Name, index_name as Index_Name,
count(*) as Page_Count, sum(data_size)/1024/1024 as Size_in_MB
from information_schema.innodb_buffer_page
WHERE table_name LIKE '%project_2%'
group by table_name, index_name
order by Size_in_MB desc)Q;

-- Inno DB Status
SHOW ENGINE INNODB STATUS

-- Einstellungen einsehen
SELECT @@innodb_buffer_pool_size/1024/1024/1024
SELECT @@innodb_buffer_pool_instances;
SELECT @@innodb_buffer_pool_chunk_size;