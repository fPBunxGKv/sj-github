---
--- https://filldb.info/dummy/step1


--- https://json-generator.com/ > evtl. besser bei django import

---       [
---         '{{repeat(120)}}',
---         {
---          model: "members.sj_users", 
---          pk: "{{index(5000)}}", 
---          fields:
---            {
---             created_at: '{{date(new Date(2014, 0, 1), new Date(), "YYYY-MM-dd hh:mm:ss")}}',
---             updated_at: '{{date(new Date(2014, 0, 1), new Date(), "YYYY-MM-dd hh:mm:ss")}}',
---             uuid: '{{guid()}}',
---             firstname: '{{firstName()}}',
---             lastname: '{{surname()}}',
---             byear: '{{integer(2008, 2019)}}',
---             gender: '{{gender()}}',
---             email: '{{email()}}',
---             phone: '+41 {{phone()}}',
---             city: '{{random("Jegenstorf", "Münchringen", "Zuzwil", "Iffwil")}}',
---             startnum: '{{integer(100000, 999999)}}',
---             state: 'YES'
---            }
---         } 
---       ]

---
--- DELETE all results / users
---
DELETE FROM members_sj_results WHERE fk_sj_events_id IN (SELECT id FROM members_sj_events WHERE uuid like 'f3750bfcac1b4fa39109e7124646908a');
--- !!! only in test database !!!! --- DELETE FROM members_sj_users;
--- 

SELECT event_date FROM members_sj_events WHERE uuid like 'f3750bfcac1b4fa39109e7124646908a';

UPDATE members_sj_users SET byear = 1900;
UPDATE members_sj_users SET byear = 2019 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2018 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2017 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2016 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2015 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2014 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2013 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2011 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2010 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2008 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'W' ORDER BY id LIMIT 6);

UPDATE members_sj_users SET byear = 2019 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2018 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2017 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2016 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2015 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2014 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2013 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2011 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2010 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
UPDATE members_sj_users SET byear = 2008 WHERE rowid IN (SELECT rowid FROM members_sj_users WHERE byear = 1900 AND gender like 'M' ORDER BY id LIMIT 6);
