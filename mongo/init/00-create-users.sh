#!/bin/bash

## we get free env 
sed -i 's/%%MONGO_READWRITE_USER%%/'"${MONGO_READWRITE_USER}"'/g' /docker-entrypoint-initdb.d/10-create-users.js
sed -i 's/%%MONGO_READWRITE_PASS%%/'"${MONGO_READWRITE_PASS}"'/g' /docker-entrypoint-initdb.d/10-create-users.js
sed -i 's/%%MONGO_READONLY_USER%%/'"${MONGO_READONLY_USER}"'/g' /docker-entrypoint-initdb.d/10-create-users.js
sed -i 's/%%MONGO_READONLY_PASS%%/'"${MONGO_READONLY_PASS}"'/g' /docker-entrypoint-initdb.d/10-create-users.js

sed -i 's/%%MONGO_DB_NAME%%/'"${MONGO_DB_NAME}"'/g' /docker-entrypoint-initdb.d/10-create-users.js
