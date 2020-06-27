
db.createUser({
    user: "%%MONGO_READWRITE_USER%%",
    pwd: "%%MONGO_READWRITE_PASS%%",
    roles: [
        {
            role: "readWrite",
            db: "%%MONGO_DB_NAME%%"
        }
    ]
});

db.createUser({
    user: "%%MONGO_READONLY_USER%%",
    pwd: "%%MONGO_READONLY_PASS%%",
    roles: [
        {
            role: "read",
            db: "%%MONGO_DB_NAME%%"
        }
    ]
});
