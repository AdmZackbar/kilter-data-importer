BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "circuit" (
	"name"	TEXT NOT NULL,
	"color"	TEXT NOT NULL DEFAULT 'x000000',
	"datecreated"	TEXT NOT NULL,
	"description"	TEXT,
	PRIMARY KEY("name")
) WITHOUT ROWID,STRICT;
CREATE TABLE IF NOT EXISTS "circuit_has_rig" (
	"circuit"	TEXT NOT NULL,
	"rig"	TEXT NOT NULL,
	PRIMARY KEY("circuit","rig"),
	CONSTRAINT "fk_circuit_has_rig_circuit" FOREIGN KEY("circuit") REFERENCES "circuit"("name")
) WITHOUT ROWID,STRICT;
CREATE TABLE IF NOT EXISTS "entry" (
	"date"	TEXT NOT NULL,
	"rig"	TEXT NOT NULL,
	"angle"	INTEGER NOT NULL,
	"burns"	INTEGER NOT NULL DEFAULT 1,
	"send"	INTEGER NOT NULL DEFAULT 1,
	"grade"	TEXT,
	"stars"	INTEGER,
	"notes"	TEXT
) STRICT;
CREATE TABLE IF NOT EXISTS "favorite" (
	"rig"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("rig")
) WITHOUT ROWID,STRICT;
CREATE TABLE IF NOT EXISTS "rig" (
	"name"	TEXT NOT NULL,
	"layout"	TEXT NOT NULL,
	"datecreated"	TEXT NOT NULL,
	"isdraft"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("name","layout")
) WITHOUT ROWID,STRICT;
CREATE TABLE IF NOT EXISTS "rig_has_hold" (
	"rig"	TEXT NOT NULL,
	"x"	INTEGER NOT NULL,
	"y"	INTEGER NOT NULL,
	"role"	TEXT NOT NULL,
	PRIMARY KEY("rig","x","y"),
	CONSTRAINT "fk_rig_has_hold_rig" FOREIGN KEY("rig") REFERENCES "rig"("name")
) WITHOUT ROWID,STRICT;
COMMIT;
