UPDATE `Users_info` 
SET
`fullname`=%s,
`age`=%s,
`experience`=%s,
`contacts`=%s,
`add`=%s
WHERE `user_id` = %s;