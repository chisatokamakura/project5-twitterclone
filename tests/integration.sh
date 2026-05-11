# set -ex:
# -e stands for "error" stop the script if there are errors 
# -x prints the contents of the script as it runs it

#!/bin/bash
set -e

BASE="http://127.0.0.1:8080"

# cleanup leftover test users from previous runs
sqlite3 ../twitter_clone.db "DELETE FROM messages WHERE sender_id IN (SELECT id FROM users WHERE username='test_auto_login');"
sqlite3 ../twitter_clone.db "DELETE FROM users WHERE username='test_auto_login';"

# basic route tests
curl -sfS "$BASE/" -o /tmp/homepage.html
grep -q "Twitter Clone" /tmp/homepage.html

curl -sfS "$BASE/login" -o /tmp/login.html
grep -q "Login" /tmp/login.html
grep -q 'type="password"' /tmp/login.html

curl -sfS "$BASE/create_user" -o /tmp/create_user.html
grep -q "Create User" /tmp/create_user.html

curl -sfS "$BASE/messages.json" -o /tmp/messages.json
grep -q "username" /tmp/messages.json

# failed login test
curl -sfS "$BASE/login?username=user0&password=wrong" \
| grep -q "Incorrect username or password"

# successful login test
curl -sfS -c cookies.txt \
"$BASE/login?username=user0&password=password0" \
> /dev/null

# create message page accessible when logged in
curl -sfS -b cookies.txt \
"$BASE/create_message" \
| grep -q "Create Message"

# logout test
curl -sfS -b cookies.txt -c cookies.txt "$BASE/logout" > /dev/null
rm cookies.txt
curl -sfSL -b /dev/null "$BASE/create_message" \
| grep -q "Login"

# re-login for rest of tests
curl -sfS -c cookies.txt \
"$BASE/login?username=user0&password=password0" \
> /dev/null

# normal message creation
curl -sfS -b cookies.txt --get \
--data-urlencode "message=hellofromtest" \
"$BASE/create_message" \
> /dev/null

curl -sfS "$BASE/" \
| grep -q "hellofromtest"

# markdown formatting test
curl -sfS -b cookies.txt --get \
--data-urlencode "message=**bold** and *italic*" \
"$BASE/create_message" \
> /dev/null

curl -sfS "$BASE/" \
| grep -q '<b>bold</b>'

# search test
curl -sfS "$BASE/search?query=hello" \
| grep -q "hellofromtest"

curl -sfS "$BASE/search?query=zzznoresultszzz" \
| grep -q "No results found"

# XSS / HTML injection test
curl -sfS -b cookies.txt --get \
--data-urlencode 'message=<script>alert("xss")</script>' \
"$BASE/create_message" \
> /dev/null

curl -sfS "$BASE/" \
| grep -q '&lt;script&gt;alert'

# SQL injection test
curl -sfS -b cookies.txt --get \
--data-urlencode "message='; DROP TABLE users; --" \
"$BASE/create_message" \
> /dev/null

curl -sfS "$BASE/" \
| grep -q "DROP TABLE users"

# verify SQL injection did NOT break database
curl -sfS \
"$BASE/login?username=user0&password=password0" \
> /dev/null

# duplicate user test
curl -sfS --get \
--data-urlencode "username=user0" \
--data-urlencode "age=78" \
--data-urlencode "password1=abc" \
--data-urlencode "password2=abc" \
"$BASE/create_user" \
| grep -q "already exists"

# password mismatch test
curl -sfS --get \
--data-urlencode "username=testuser" \
--data-urlencode "age=20" \
--data-urlencode "password1=abc" \
--data-urlencode "password2=xyz" \
"$BASE/create_user" \
| grep -q "Passwords do not match"

# URL should become clickable link
curl -sfS -b cookies.txt --get \
--data-urlencode "message=check_this_link https://example.com" \
"$BASE/create_message" \
> /dev/null

curl -sfS "$BASE/" \
| grep -q '<a href="https://example.com">https://example.com</a>'

# verify robohash images appear
curl -sfS "$BASE/" \
| grep -q "https://robohash.org/"

# verify database population counts
sqlite3 ../twitter_clone.db \
"SELECT COUNT(*) FROM users;" \
| grep -E "^[2-9][0-9][0-9]$"

sqlite3 ../twitter_clone.db \
"SELECT COUNT(*) FROM messages;" \
| grep -E "^[4-9][0-9][0-9][0-9][0-9]$"

# create new account auto-login test
curl -sfSL -c newcookies.txt --get \
--data-urlencode "username=test_auto_login" \
--data-urlencode "age=20" \
--data-urlencode "password1=abc" \
--data-urlencode "password2=abc" \
"$BASE/create_user" \
> /dev/null

curl -sfS -b newcookies.txt \
"$BASE/create_message" \
| grep -q "Create Message"

# change password test
curl -sfS -b newcookies.txt --get \
--data-urlencode "old_password=abc" \
--data-urlencode "new_password1=xyz" \
--data-urlencode "new_password2=xyz" \
"$BASE/change_password" \
> /dev/null

# verify old password no longer works
curl -sfS \
"$BASE/login?username=test_auto_login&password=abc" \
| grep -q "Incorrect username or password"

# verify new password DOES work
curl -sfS -c changedcookies.txt \
"$BASE/login?username=test_auto_login&password=xyz" \
> /dev/null

curl -sfS -b changedcookies.txt \
"$BASE/create_message" \
| grep -q "Create Message"

# create editable message
curl -sfS -b changedcookies.txt --get \
--data-urlencode "message=messagetoedit" \
"$BASE/create_message" \
> /dev/null

# find created message id
MESSAGE_ID=$(sqlite3 ../twitter_clone.db \
"SELECT id FROM messages WHERE message='messagetoedit' ORDER BY id DESC LIMIT 1;")

# edit message test
curl -sfS -b changedcookies.txt --get \
--data-urlencode "message_id=$MESSAGE_ID" \
--data-urlencode "message=edited_message" \
"$BASE/edit_message" \
> /dev/null

curl -sfS "$BASE/" \
| grep -q "edited_message"

curl -sfS "$BASE/" \
| grep -q "Edited at"

# delete message test
curl -sfS -b changedcookies.txt \
"$BASE/delete_message?message_id=$MESSAGE_ID" \
> /dev/null

if curl -sfS "$BASE/" | grep -q "edited_message"; then
    echo "Delete message failed"
    exit 1
fi

# delete user test
curl -sfS -b changedcookies.txt \
"$BASE/delete_user" \
> /dev/null

curl -sfS \
"$BASE/login?username=test_auto_login&password=xyz" \
| grep -q "Incorrect username or password"

# pagination test
curl -sfS "$BASE/?page=1" \
| grep -q "Twitter Clone"

curl -sfS "$BASE/?page=0" \
| grep -q "← Previous" || true

curl -sfS "$BASE/?page=1" \
| grep -q "← Previous"

# verify json endpoint returns JSON-like structure
curl -sfS "$BASE/messages.json" \
| grep -q '"username"'

curl -sfS "$BASE/messages.json" \
| grep -q '"message"'

echo "All integration tests passed!"