CREATE TABLE Merkmal (
  ID           int NOT NULL IDENTITY(1,1), 
  Bezeichnung  varchar(255) NOT NULL, 
  Beschreibung varchar(255),
  Datentyp 	varchar(255),
  PRIMARY KEY (ID));
  
CREATE TABLE Merkmalsauspr�gung (
  ID         int NOT NULL IDENTITY(1,1), 
  MerkmalID  int NOT NULL, 
  Auspr�gung varchar(255) NOT NULL, 
  PRIMARY KEY (ID));
  
CREATE TABLE SNR (
  ID 	int NOT NULL IDENTITY(1,1),
  SNR 	char(18) NULL,
  FA	char(20) NULL,
  TEIL	char(1) NULL,
  LINIE char(1) NULL,
  PRIMARY KEY (ID));

CREATE TABLE R�ckmeldung (
  ID 		int NOT NULL IDENTITY(1,1),
  SNR		char(18) NULL,
  LINIE 	char(1) NULL,
  SNR_ID 	int NULL,
  PRIMARY KEY (ID));
  
CREATE TABLE FA (
  FA	char(20) NOT NULL,
  PRIMARY KEY (FA));
  
CREATE TABLE TEIL (
  TEIL	char(1) NOT NULL,
  PRIMARY KEY (TEIL));

CREATE TABLE LINIE (
  LINIE	char(1) NOT NULL,
  PRIMARY KEY (LINIE));
  
CREATE TABLE Objekt2Merkmal (
  ID        int NOT NULL IDENTITY(1,1), 
  MerkmalID int NOT NULL, 
  ObjektID  int NOT NULL, 
  ObjektTyp int NOT NULL, 
  PRIMARY KEY (ID));
  
CREATE TABLE Objekt2Merkmalsauspr�gung (
  ID                   int NOT NULL IDENTITY(1,1), 
  Merkmalsauspr�gungID int NOT NULL, 
  ObjektID             int NOT NULL, 
  ObjektTyp            int NOT NULL, 
  PRIMARY KEY (ID));
  
CREATE TABLE ObjektTyp (
  ID			int NOT NULL IDENTITY(1,1),
  Bezeichnung	char(255) NOT NULL,
  Beschreibung 	char(255),
  PRIMARY KEY (ID));
  
ALTER TABLE Objekt2Merkmal ADD FOREIGN KEY (MerkmalID) REFERENCES Merkmal (ID);
ALTER TABLE Objekt2Merkmal ADD FOREIGN KEY (ObjektTyp) REFERENCES ObjektTyp(ID);


ALTER TABLE Objekt2Merkmalsauspr�gung ADD FOREIGN KEY (Merkmalsauspr�gungID) REFERENCES Merkmalsauspr�gung (ID);
ALTER TABLE Objekt2Merkmalsauspr�gung ADD FOREIGN KEY (ObjektTyp) REFERENCES ObjektTyp(ID);


ALTER TABLE Merkmalsauspr�gung ADD FOREIGN KEY (MerkmalID) REFERENCES Merkmal (ID);


ALTER TABLE SNR ADD FOREIGN KEY (TEIL) REFERENCES TEIL (TEIL);
ALTER TABLE SNR ADD FOREIGN KEY (FA) REFERENCES FA (FA);
ALTER TABLE SNR ADD FOREIGN KEY (LINIE) REFERENCES LINIE (LINIE);


ALTER TABLE R�ckmeldung ADD FOREIGN KEY (SNR_ID) REFERENCES SNR (ID);
ALTER TABLE R�ckmeldung ADD FOREIGN KEY (LINIE) REFERENCES LINIE (LINIE);


CREATE INDEX INDEX_TBL_SNR ON SNR (SNR);
CREATE INDEX INDEX_TBL_SNR2 ON SNR (TEIL) INCLUDE (FA);
CREATE INDEX INDEX_TBL_SNR3 ON SNR (FA, SNR);
CREATE INDEX INDEX_TBL_SNR4 ON SNR (TEIL,SNR);
CREATE INDEX INDEX_TBL_SNR5 ON SNR (LINIE) INCLUDE (FA);

CREATE INDEX INDEX_TBL_MA ON Merkmalsauspr�gung (MerkmalID) INCLUDE (Auspr�gung) WHERE MerkmalID = 21;
CREATE INDEX INDEX_TBL_MA2 ON Merkmalsauspr�gung (MerkmalID, Auspr�gung);
CREATE INDEX INDEX_TBL_MA3 ON Merkmalsauspr�gung (MerkmalID) INCLUDE (Auspr�gung) WHERE MerkmalID = 1;
CREATE INDEX INDEX_TBL_MA4 ON Merkmalsauspr�gung (MerkmalID) INCLUDE (Auspr�gung) WHERE MerkmalID = 39;


CREATE INDEX INDEX_TBL_O2MA ON Objekt2Merkmalsauspr�gung (ObjektID, ObjektTyp) INCLUDE (Merkmalsauspr�gungID);
CREATE INDEX INDEX_TBL_O2MA2 ON Objekt2Merkmalsauspr�gung (ObjektTyp) INCLUDE (Merkmalsauspr�gungID, ObjektID);
CREATE INDEX INDEX_TBL_O2MA3 ON Objekt2Merkmalsauspr�gung (Merkmalsauspr�gungID, ObjektTyp) INCLUDE (ObjektID);


CREATE INDEX INDEX_TBL_O2M ON Objekt2Merkmal (ObjektID, ObjektTyp);
CREATE INDEX INDEX_TBL_O2M2 ON Objekt2Merkmal (MerkmalID, ObjektID, ObjektTyp);

CREATE INDEX INDEX_TBL_R�ck ON R�ckmeldung (SNR);
CREATE INDEX INDEX_TBL_R�ck2 ON R�ckmeldung (SNR_ID);






















