# MongoDB and FastAPI

Edit your `.env` file in project dir.

## Dev

```bash
docker logs fastapi-app
docker exec -it fastapi-app bash

curl -X POST "http://localhost:8000/items/" -H "Content-Type: application/json" -d '{"name": "NewItem"}'
```

Connect with mongosh

```bash
docker run -it --rm --network some-network mongo \
	mongosh --host some-mongo \
		-u mongoadmin \
		-p secret \
		--authenticationDatabase admin \
		some-db
        
> db.getName();
some-db
```

## Backups

```bash
docker exec -it mongo-exapp bash
mongodump --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --out /backup
docker cp mongo-exapp:/backup ./backups
```
