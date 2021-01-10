CREATE TABLE Merkmal (
  ID           int NOT NULL IDENTITY(1,1), 
  Bezeichnung  varchar(255) NOT NULL, 
  Beschreibung varchar(255),
  Datentyp 	varchar(255),
  PRIMARY KEY (ID));
  
CREATE TABLE Merkmalsausprägung (
  ID         int NOT NULL IDENTITY(1,1), 
  MerkmalID  int NOT NULL, 
  Ausprägung varchar(255) NOT NULL, 
  PRIMARY KEY (ID));
  
CREATE TABLE SNR (
  ID 	int NOT NULL IDENTITY(1,1),
  SNR 	char(18) NULL,
  FA	char(20) NULL,
  TEIL	char(1) NULL,
  LINIE char(1) NULL,
  PRIMARY KEY (ID));

CREATE TABLE Rückmeldung (
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
  
CREATE TABLE Objekt2Merkmalsausprägung (
  ID                   int NOT NULL IDENTITY(1,1), 
  MerkmalsausprägungID int NOT NULL, 
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


ALTER TABLE Objekt2Merkmalsausprägung ADD FOREIGN KEY (MerkmalsausprägungID) REFERENCES Merkmalsausprägung (ID);
ALTER TABLE Objekt2Merkmalsausprägung ADD FOREIGN KEY (ObjektTyp) REFERENCES ObjektTyp(ID);


ALTER TABLE Merkmalsausprägung ADD FOREIGN KEY (MerkmalID) REFERENCES Merkmal (ID);


ALTER TABLE SNR ADD FOREIGN KEY (TEIL) REFERENCES TEIL (TEIL);
ALTER TABLE SNR ADD FOREIGN KEY (FA) REFERENCES FA (FA);
ALTER TABLE SNR ADD FOREIGN KEY (LINIE) REFERENCES LINIE (LINIE);


ALTER TABLE Rückmeldung ADD FOREIGN KEY (SNR_ID) REFERENCES SNR (ID);
ALTER TABLE Rückmeldung ADD FOREIGN KEY (LINIE) REFERENCES LINIE (LINIE);


CREATE INDEX INDEX_TBL_SNR ON SNR (SNR);
CREATE INDEX INDEX_TBL_SNR2 ON SNR (TEIL) INCLUDE (FA);
CREATE INDEX INDEX_TBL_SNR3 ON SNR (FA, SNR);
CREATE INDEX INDEX_TBL_SNR4 ON SNR (TEIL,SNR);
CREATE INDEX INDEX_TBL_SNR5 ON SNR (LINIE) INCLUDE (FA);

CREATE INDEX INDEX_TBL_MA ON Merkmalsausprägung (MerkmalID) INCLUDE (Ausprägung) WHERE MerkmalID = 21;
CREATE INDEX INDEX_TBL_MA2 ON Merkmalsausprägung (MerkmalID, Ausprägung);
CREATE INDEX INDEX_TBL_MA3 ON Merkmalsausprägung (MerkmalID) INCLUDE (Ausprägung) WHERE MerkmalID = 1;
CREATE INDEX INDEX_TBL_MA4 ON Merkmalsausprägung (MerkmalID) INCLUDE (Ausprägung) WHERE MerkmalID = 39;


CREATE INDEX INDEX_TBL_O2MA ON Objekt2Merkmalsausprägung (ObjektID, ObjektTyp) INCLUDE (MerkmalsausprägungID);
CREATE INDEX INDEX_TBL_O2MA2 ON Objekt2Merkmalsausprägung (ObjektTyp) INCLUDE (MerkmalsausprägungID, ObjektID);
CREATE INDEX INDEX_TBL_O2MA3 ON Objekt2Merkmalsausprägung (MerkmalsausprägungID, ObjektTyp) INCLUDE (ObjektID);


CREATE INDEX INDEX_TBL_O2M ON Objekt2Merkmal (ObjektID, ObjektTyp);
CREATE INDEX INDEX_TBL_O2M2 ON Objekt2Merkmal (MerkmalID, ObjektID, ObjektTyp);

CREATE INDEX INDEX_TBL_Rück ON Rückmeldung (SNR);
CREATE INDEX INDEX_TBL_Rück2 ON Rückmeldung (SNR_ID);






















